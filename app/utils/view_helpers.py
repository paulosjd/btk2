from app.models import ProfileParamUnitOption


def param_unit_opt_dct(unit_opt):
    return {f'unit_{field}': getattr(unit_opt, field)
            for field in ['symbol', 'name', 'param_default',
                          'conversion_factor']}


def get_summary_data(profile):
    fields = ['name', 'upload_fields', 'upload_field_labels', 'ideal_info',
              'ideal_info_url', 'num_values'] + [f'value2_short_label_{i}'
                                                 for i in [1, 2]]
    summary_qs = profile.summary_data()
    return [{
        'parameter': {
            **{field: getattr(obj.parameter, field) for field in fields},
            **param_unit_opt_dct(
                ProfileParamUnitOption.get_unit_option(
                    profile, summary_qs[i].parameter)
            )},
        'data_point': {field: getattr(obj, field)
                       for field in ['date', 'value', 'value2']},
    } for i, obj in enumerate(summary_qs)]
