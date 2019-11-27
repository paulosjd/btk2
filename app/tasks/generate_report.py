import base64
import io
from operator import itemgetter

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from celery.utils.log import get_task_logger
from django.template.loader import get_template
from matplotlib import style
from xhtml2pdf import pisa

from app.models import Profile, ProfileParamUnitOption
from app.utils import get_monthly_means, get_rolling_mean
from btk2.celery import celery_app

log = get_task_logger(__name__)


# @celery_app.task
def profile_report_pdf(profile_id, date='20th Feb 2018'):
    try:
        profile = Profile.objects.get(id=profile_id)
    except Profile.DoesNotExist as e:
        log.error(e)
        return
    report_data = {
        'items_list': get_items_list(profile.all_datapoints(), profile),
        'date': date
    }
    pdf = render_to_pdf('profile_report.html', report_data)
    with open('foobar.pdf', 'wb') as file:
        file.write(pdf)


def render_to_pdf(template_src, context_dct):
    template = get_template(template_src)
    html = template.render(context_dct)
    result = io.BytesIO()
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return result.getvalue()
    log.error(pdf.error)


def get_items_list(all_dps, profile):
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
    items_list = [{
        'name': name,
        'unit_symbol': unit_symbols[ind],
        'val2_label_1': lab1,
        'val2_label_2': lab2,
        'has_val2': has_val2,
        'records': [{k: getattr(obj, k) for k in ['date', 'value', 'value2']}
                    for obj in all_dps if obj.parameter.name == name]
    } for ind, (name, has_val2, lab1, lab2, _) in enumerate(param_names)]
    for ind, item in enumerate(items_list):
        dps, extra = [{k: dct[k] for k in ['date', 'value', 'value2']}
                      for dct in item['records']], {'param_name': item['name']}
        items_list[ind].update({
            'rolling_means': get_rolling_mean(dps, extra=extra),
            'monthly_means': get_monthly_means(dps, extra=extra)
        })

        prm_fiels = ['unit_symbol', 'has_val2', 'val2_label_1', 'val2_label_2']
        recs_plot = None
        if len(item['records']) > 3:
            plot_bio = make_chart_from_data(
                item['records'], key='', **{k: item[k] for k in prm_fiels}
            )
            recs_plot = base64.b64encode(plot_bio.getvalue()).decode('ascii')
        rms_plot = None
        rms = get_rolling_mean(dps, extra=extra)
        if len(rms) > 3:
            plot_bio = make_chart_from_data(
                rms, key='rolling_means', **{k: item[k] for k in prm_fiels}
            )
            rms_plot = base64.b64encode(plot_bio.getvalue()).decode('ascii')
        mms_plot = None
        mms = get_monthly_means(dps, extra=extra)
        if len(mms) > 3:
            plot_bio = make_chart_from_data(
                mms, key='monthly_means', **{k: item[k] for k in prm_fiels}
            )
            mms_plot = base64.b64encode(plot_bio.getvalue()).decode('ascii')

        items_list[ind].update({
            'records_plot': recs_plot,
            'rolling_means_plot': rms_plot,
            'monthly_means_plot': mms_plot
        })
    return items_list


def make_chart_from_data(means_data, key='', **kwargs):
    title_map = {'rolling_means': 'Moving averages',
                 'monthly_means': 'Monthly averages'}
    fig = plt.figure(figsize=(7, 3))
    plt.title(title_map.get(key, ''), fontsize=14, fontname='Arial', loc='left',
              pad=3)
    plt.ylabel(kwargs.get('unit_symbol', ''), fontname='Arial', fontsize=12)
    dtf = '%Y-%m-%d'
    if key != 'rolling_means':
        dtf = '%Y-%b'
    df = pd.DataFrame(
        {pd.datetime.strptime(d['date'], dtf): [d.get(f'value{i}', '')
                                                for i in ['', 2]]
         for d in means_data[::-1]},
        index=[kwargs.get(f'val2_label_{a}', f'value {a}') for a in [1, 2]]
    )
    ss = df.iloc[0, :]
    ss.plot(color="coral", linewidth=2, linestyle="-")
    # ss.plot(figsize=(10, 6), color="coral", linewidth=2, linestyle="-")
    if kwargs.get('has_val2'):
        ss2 = df.iloc[1, :]
        ss2.plot(color="cornflowerblue", linewidth=2, linestyle="-")
        plt.legend(loc='upper right', fontsize='small')
    bio = io.BytesIO()
    # save figure to bytesio
    fig.savefig(bio, format="png", bbox_inches='tight')
    # plt.show()
    plt.clf()
    plt.close(fig)
    return bio


# rms = [
#     {'date': '2019-09-09', 'value': 29.0, 'param_name': 'Blood cholesterol', 'value2': 41.0},
#     {'date': '2019-07-09', 'value': 28.3, 'param_name': 'Blood cholesterol', 'value2': 41.3},
#     {'date': '2019-04-09', 'value': 28.8, 'param_name': 'Blood cholesterol', 'value2': 40.0},
#     {'date': '2019-01-24', 'value': 28.2, 'param_name': 'Blood cholesterol', 'value2': 40.0},
#     {'date': '2018-10-10', 'value': 28.5, 'param_name': 'Blood cholesterol', 'value2': 40.0},
#     {'date': '2018-09-19', 'value': 28.5, 'param_name': 'Blood cholesterol', 'value2': 39.8},
#     {'date': '2018-05-10', 'value': 27.2, 'param_name': 'Blood cholesterol', 'value2': 39.5},
#     {'date': '2017-10-10', 'value': 27.2, 'param_name': 'Blood cholesterol', 'value2': 38.8},
#     {'date': '2016-04-11', 'value': 27.2, 'param_name': 'Blood cholesterol', 'value2': 37.0},
#     {'date': '2015-10-11', 'value': 30.5, 'param_name': 'Blood cholesterol', 'value2': 39.2}
# ]