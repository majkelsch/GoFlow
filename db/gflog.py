from sqlalchemy import event, inspect
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class DBChangeLog(Base):
    __tablename__ = 'db_change_log'

    log_id = Column(Integer, primary_key=True)
    table_name = Column(String, nullable=False)
    record_id = Column(Integer, nullable=False)
    action_type = Column(String, nullable=False)
    old_data = Column(JSON, nullable=True)
    new_data = Column(JSON, nullable=True)
    changed_at = Column(DateTime, default=datetime.utcnow)
    changed_by = Column(String, nullable=True)

def serialize_instance(instance):
    def convert_value(value):
        if isinstance(value, datetime):
            return value.isoformat()
        return value

    return {
        c.key: convert_value(getattr(instance, c.key))
        for c in inspect(instance).mapper.column_attrs
    }


def attach_logger(model_class, session, user_getter=lambda: 'system'):
    if not hasattr(session, "_change_log_queue"):
        session._change_log_queue = []

    @event.listens_for(model_class, 'after_insert')
    def collect_insert(mapper, connection, target):
        new_data = serialize_instance(target)
        session._change_log_queue.append(DBChangeLog(
            table_name=target.__tablename__,
            record_id=new_data.get('id', -1),
            action_type='INSERT',
            new_data=new_data,
            changed_by=user_getter()
        ))

    @event.listens_for(model_class, 'before_update')
    def collect_update(mapper, connection, target):
        state = inspect(target)
        if not state.modified:
            return
        old_data = {
            attr.key: state.attrs[attr.key].history.deleted[0]
            for attr in mapper.attrs
            if state.attrs[attr.key].history.has_changes()
        }
        new_data = serialize_instance(target)
        session._change_log_queue.append(DBChangeLog(
            table_name=target.__tablename__,
            record_id=new_data.get('id', -1),
            action_type='UPDATE',
            old_data=old_data,
            new_data=new_data,
            changed_by=user_getter()
        ))

    @event.listens_for(model_class, 'before_delete')
    def collect_delete(mapper, connection, target):
        old_data = serialize_instance(target)
        session._change_log_queue.append(DBChangeLog(
            table_name=target.__tablename__,
            record_id=old_data.get('id', -1),
            action_type='DELETE',
            old_data=old_data,
            changed_by=user_getter()
        ))

    @event.listens_for(session, 'after_flush')
    def flush_log_entries(session, flush_context):
        if hasattr(session, "_change_log_queue"):
            for log_entry in session._change_log_queue:
                session.add(log_entry)
            session._change_log_queue.clear()

