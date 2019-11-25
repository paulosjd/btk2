import io
from operator import itemgetter

import seaborn as sns
from celery.utils.log import get_task_logger
from django.template.loader import get_template
from xhtml2pdf import pisa

from app.models import Parameter, Profile, ProfileParamUnitOption
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
    pdf = pisa.pisaDocument(io.BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        log.info('Result getvalue')
        log.info(result.getvalue())
        log.info(type(result.getvalue()))
        return result.getvalue()


def get_items_list(all_dps, profile):
    dp_lst = [{**{k: getattr(obj, k) for k in ['date', 'value', 'value2']},
               'parameter': obj.parameter.name} for obj in all_dps]
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
        'unit_symbol': ind,
        'val2_label_1': lab1,
        'val2_label_2': lab2,
        'has_val2': has_val2,
        'records': [{k: dct[k] for k in ['date', 'value', 'value2']}
                    for dct in dp_lst if dct['parameter'] == name]
    } for ind, (name, has_val2, lab1, lab2, _) in enumerate(param_names)]
    for ind, item in enumerate(items_list):
        dps, extra = [{k: dct[k] for k in ['date', 'value', 'value2']}
                      for dct in item['records']], {'param_name': item['name']}
        items_list[ind].update({
            'rolling_means': get_rolling_mean(dps, extra=extra),
            'monthly_changes': get_monthly_means(dps, extra=extra)
        })
    print(items_list)
    return items_list
