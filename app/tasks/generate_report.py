import base64
import datetime
import io
import os
from operator import itemgetter
from tempfile import NamedTemporaryFile
from typing import List, NamedTuple, Optional, Sequence

import matplotlib.pyplot as plt
import pandas as pd
from celery.utils.log import get_task_logger
from django.template.loader import get_template
from matplotlib.ticker import FormatStrFormatter
from xhtml2pdf import pisa

from app.models import Profile, ProfileParamUnitOption
from app.utils import get_monthly_means, get_rolling_mean
from btk2.celery import celery_app

log = get_task_logger(__name__)


@celery_app.task
def profile_report_pdf(profile_id, date_str='',
                       param_ids: List[int] = None,
                       removed_stats: List[str] = None) -> Optional[str]:
    removed_stats = removed_stats or []
    current_file = os.path.abspath(os.path.dirname(__file__))
    tmp_folder = os.path.join(current_file, 'report_temp')
    profile = Profile.objects.filter(id=profile_id).first()
    if not profile or not param_ids:
        return
    today = None
    try:
        today = datetime.datetime.strptime(date_str, '%b %d %Y')
    except ValueError:
        pass

    report_data = {
        'items_list': get_items_list(
            profile.all_datapoints().filter(parameter_id__in=param_ids),
            profile,
            removed_stats=removed_stats
        ),
        'date': today or datetime.date.today()
    }

    pdf = render_to_pdf('profile_report.html', report_data)
    file = NamedTemporaryFile(
        suffix='report.pdf', dir=tmp_folder, delete=False
    )
    with open(file.name, 'wb') as f:
        f.write(pdf)

    return file.name


def render_to_pdf(template_src, context_dct) -> Optional[bytes]:
    template = get_template(template_src)
    html = template.render(context_dct)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("utf-8")), result)
    if not pdf.err:
        return result.getvalue()
    log.error(pdf.error)


def get_items_list(all_dps: List[object], profile: object,
                   removed_stats: List[str]) -> List[dict]:
    prm_fiels = 'unit_symbol', 'has_val2', 'val2_label_1', 'val2_label_2'
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

    for ind, item in enumerate(items_list):
        dps, extra = [{k: dct[k] for k in ['date', 'value', 'value2']}
                      for dct in item['records']], {'param_name': item['name']}

        plot_items = [(item['records'], 'records')]
        for k, fn in [('rolling', get_rolling_mean),
                      ('monthly', get_monthly_means)]:
            if k not in removed_stats:
                plot_items.append(
                    (fn(dps, extra=extra), f'{k}_means')
                )

        plots = {}
        for data_set, stat_key in plot_items:
            if len(data_set) > 3:
                plot_bio = make_chart_from_data(
                    data_set, stat=stat_key,
                    **{k: item[k] for k in prm_fiels}
                )
                if plot_bio:
                    plots[stat_key] = base64.b64encode(plot_bio.getvalue()
                                                       ).decode('ascii')
        items_list[ind].update(
            {f'{k}_plot': plots.get(k) for k in
             ['records', 'rolling_means', 'monthly_means']}
        )

    return items_list


def make_chart_from_data(means_data, stat='', **kwargs) -> Optional[io.BytesIO]:
    title_map = {'rolling_means': 'Moving averages',
                 'monthly_means': 'Monthly averages (12 months)'}
    fig, ax = plt.subplots(figsize=(7, 2.5))
    ax.yaxis.set_major_formatter(FormatStrFormatter('%.0f'))
    plt.title(title_map.get(stat, ''), fontsize=11, fontname='Arial',
              loc='left', pad=6)
    plt.ylabel(kwargs.get('unit_symbol', ''), fontname='Arial', fontsize=11)
    dtf, key = ('%Y-%m-%d', 'date') if stat != 'monthly' else ('%Y-%b', 'month')

    df = pd.DataFrame(
        {pd.datetime.strptime(d[key], dtf)
         if stat != 'records' else pd.to_datetime(datetime.datetime.combine(
            d[key], datetime.time())):
            [d.get(f'value{i}', '') for i in ['', 2]]
         for d in means_data[::-1] if d.get(key)},
        index=[kwargs.get(f'val2_label_{a}', f'value {a}') for a in [1, 2]]
    )
    ss = df.iloc[0, :]
    try:
        ss.plot(color="#8a3b78")
    except TypeError:
        return
    if kwargs.get('has_val2'):
        ss2 = df.iloc[1, :]
        try:
            ss2.plot(color="#c25476")
        except TypeError:
            return
        plt.legend(loc='upper right', fontsize='small')

    bio = io.BytesIO()
    fig.savefig(bio, format="png", bbox_inches='tight')
    plt.close(fig)
    return bio


ParamInfo = NamedTuple('p_info', [('names', Sequence), ('symbols', list)])


def get_param_info(all_dps: List[object], profile: object) -> ParamInfo:
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
