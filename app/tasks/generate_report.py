import io

import seaborn as sns
from celery.utils.log import get_task_logger
from django.template import Context
from django.template.loader import get_template
from xhtml2pdf import pisa

from app.models import Profile
from app.utils import get_monthly_means, get_rolling_mean
from btk2.celery import celery_app

log = get_task_logger(__name__)


# @celery_app.task
def profile_report_pdf(profile_id):
    try:
        profile = Profile.objects.get(id=profile_id)
    except Profile.DoesNotExist as e:
        log.error(e)
        return
    report_data = {
        'items_list': get_items_list(profile.all_datapoints())
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


def get_items_list(all_dps):
    dp_dct = {
        'datapoints': [{**{field: getattr(obj, field) for field in
                           ['date', 'value', 'value2']},
                        **{'parameter': obj.parameter.name,
                           'num_values': obj.parameter.num_values}}
                       for obj in all_dps]
    }
    param_names = sorted(set([obj.parameter.name for obj in all_dps]))
    items_list = [{
        'name': name,
        'records': [{k: dct[k] for k in ['date', 'value', 'value2']}
                    for dct in dp_dct['datapoints'] if dct['parameter'] == name]
    } for name in param_names]
    for ind, item in enumerate(items_list):
        dps, extra = [{k: dct[k] for k in ['date', 'value', 'value2']}
                      for dct in item['records']], {'param_name': item['name']}
        items_list[ind].update({
            'rolling_means': get_rolling_mean(dps, extra=extra),
            'monthly_changes': get_monthly_means(dps, extra=extra)
        })
    return items_list
