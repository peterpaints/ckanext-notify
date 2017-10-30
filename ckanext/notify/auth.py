import ckan.lib.helpers as helpers


def manage_notifications(context, data_dict):
    my_organizations = helpers.organizations_available()
    can_manage = [org['name'] for org in my_organizations]
    return {'success': data_dict['organization_id'] in can_manage}
