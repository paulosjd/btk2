import base64
import datetime
import io
from operator import itemgetter
from typing import List, NamedTuple, Optional, Sequence

import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import pandas as pd
from celery.utils.log import get_task_logger
from django.template.loader import get_template
from xhtml2pdf import pisa

from app.models import Profile, ProfileParamUnitOption
from app.utils import get_monthly_means, get_rolling_mean
from btk2.celery import celery_app

log = get_task_logger(__name__)


# @celery_app.task
def profile_report_pdf(profile_id, date='20th Feb 2018'):
    profile = Profile.objects.filter(id=profile_id).first()
    if not profile:
        return
    report_data = {
        'items_list': get_items_list(profile.all_datapoints(), profile),
        'date': date
    }
    pdf = render_to_pdf('profile_report.html', report_data)
    with open('foobar.pdf', 'wb') as file:
        file.write(pdf)


def render_to_pdf(template_src, context_dct) -> Optional[bytes]:
    template = get_template(template_src)
    html = template.render(context_dct)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("utf-8")), result)
    if not pdf.err:
        return result.getvalue()
    log.error(pdf.error)


def get_items_list(all_dps, profile) -> List[dict]:
    param_info = get_param_info(all_dps, profile)
    items_list = [{
        'name': name,
        'unit_symbol': param_info.symbols[ind],
        'val2_label_1': lab1,
        'val2_label_2': lab2,
        'has_val2': has_val2,
        'records': [{k: getattr(obj, k) for k in ['date', 'value', 'value2']}
                    for obj in all_dps if obj.parameter.name == name]
    } for ind, (name, has_val2, lab1, lab2, _) in enumerate(param_info.names)]

    prm_fiels = 'unit_symbol', 'has_val2', 'val2_label_1', 'val2_label_2'
    for ind, item in enumerate(items_list):
        dps, extra = [{k: dct[k] for k in ['date', 'value', 'value2']}
                      for dct in item['records']], {'param_name': item['name']}

        # TODO make dry
        plots = {}

        for data_set, stat_key in [
            (item['records'], 'recs'),
            (get_rolling_mean(dps, extra=extra), 'rolling'),
            (get_monthly_means(dps, extra=extra), 'monthly')
        ]:
            if len(data_set) > 3:
                plot_bio = make_chart_from_data(
                    data_set, stat=stat_key, **{k: item[k] for k in prm_fiels}
                )
                if plot_bio:
                    plots[stat_key] = base64.b64encode(plot_bio.getvalue()
                                                       ).decode('ascii')



        items_list[ind].update({
            'records_plot': plots.get('recs'),
            'rolling_means_plot': plots.get('rolling'),
            'monthly_means_plot': plots.get('monthly'),
        })
    return items_list


def make_chart_from_data(means_data, stat='', **kwargs) -> Optional[io.BytesIO]:
    title_map = {'rolling': 'Moving averages',
                 'monthly': 'Monthly averages (12 months)'}
    fig, ax = plt.subplots(figsize=(6.5, 2.5))
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.0f'))
    plt.title(title_map.get(stat, ''), fontsize=14, fontname='Arial',
              loc='left', pad=3)
    plt.ylabel(kwargs.get('unit_symbol', ''), fontname='Arial', fontsize=7)
    dtf, key = ('%Y-%m-%d', 'date') if stat != 'monthly' else ('%Y-%b', 'month')

    df = pd.DataFrame(
        {pd.datetime.strptime(d[key], dtf)
         if stat != 'recs' else pd.to_datetime(datetime.datetime.combine(
            d[key], datetime.time())):
            [d.get(f'value{i}', '') for i in ['', 2]]
         for d in means_data[::-1] if d.get(key)},
        index=[kwargs.get(f'val2_label_{a}', f'value {a}') for a in [1, 2]]
    )
    ss = df.iloc[0, :]
    try:
        ss.plot(color="#8a3b78", linewidth=2, linestyle="-")
    except TypeError:
        return
    if kwargs.get('has_val2'):
        ss2 = df.iloc[1, :]
        try:
            ss2.plot(color="#c25476", linewidth=2, linestyle="-")
        except TypeError:
            return
        plt.legend(loc='upper right', fontsize='small')
    bio = io.BytesIO()
    fig.savefig(bio, format="png", bbox_inches='tight')
    plt.close(fig)
    return bio


ParamInfo = NamedTuple('p_info', [('names', Sequence), ('symbols', list)])


def get_param_info(all_dps: list, profile: object) -> ParamInfo:
    param_names = sorted(
        set([(obj.parameter.name,
              obj.parameter.num_values == 2,
              obj.parameter.value2_short_label_1,
              obj.parameter.value2_short_label_2,
              obj.parameter.custom_symbol)
             for obj in all_dps]),
        key=itemgetter(0)
    )
    unit_symbols = []
    for tpl in param_names:
        symbol = tpl[4]
        if not symbol:
            try:
                symbol = ProfileParamUnitOption.objects.get(
                    parameter__name=tpl[0], profile=profile
                ).unit_option.symbol
            except ProfileParamUnitOption.DoesNotExist as e:
                log.error(e)
                symbol = 'n/a'
        unit_symbols.append(symbol)
    return ParamInfo(param_names, unit_symbols)
