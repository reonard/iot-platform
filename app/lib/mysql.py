from sqlalchemy import event, inspect
from sqlalchemy.orm.query import Query

# 注册全局查询过滤


def register_filter():

    from app.models.device import Device
    from app.models.customer import Customer
    from app.models.issue_config import IssueMsg
    from app.lib.auth import current_user_info

    @event.listens_for(Query, "before_compile", retval=True)
    def before_compile(query):

        if query._execution_options.get("include_all", False):
            return query

        for ent in query.column_descriptions:

            entity = ent['entity']
            if entity is None:
                continue

            insp = inspect(ent['entity'])
            mapper = getattr(insp, 'mapper', None)
            if mapper and mapper.class_ == Device:
                query = query.enable_assertions(False).join(Customer).\
                    filter(Customer.name.in_(current_user_info.viewable_projects))
            if mapper and mapper.class_ == IssueMsg:
                query = query.enable_assertions(False).filter(IssueMsg.created_by == current_user_info.id)

        return query
