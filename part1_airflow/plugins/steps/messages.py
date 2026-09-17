from airflow.models import Variable
from airflow.providers.telegram.hooks.telegram import TelegramHook


def _get_telegram_hook():
    """
    Создание Telegram хука из значений, хранящихся в Airflow Variables.
    """
    token = Variable.get('telegram_token')
    chat_id = Variable.get('telegram_chat_id')
    return TelegramHook(token=token, chat_id=chat_id), chat_id


def send_telegram_message(context: dict, success: bool) -> None:
    """
    Отправка сообщения в Telegram.

    :param contex: контекст DAG.
    :param success: True если DAG завершился успешно, иначе False.

    :return: None.
    """
    hook, chat_id = _get_telegram_hook()

    dag = context['dag']
    dag_id = dag if isinstance(dag, str) else dag.dag_id
    run_id = context['run_id']

    if success:
        message = f'Исполнение DAG {dag_id} с id={run_id} прошло успешно!'
    else:
        message = (
            f'Исполнение DAG {dag_id} с id={run_id} завершилось неудачно!\n'
            f'Упавшая таска: {context.get("task_instance_key_str", "неизвестно")}'
        )
    
    hook.send_message({
        'chat_id': chat_id,
        'text': message
    })
    

def send_telegram_success_message(context) -> None:
    """
    Отправка сообщение об успехе в Telegram.

    :param contex: контекст DAG.

    :return: None.
    """
    send_telegram_message(contex, True)


def send_telegram_failure_message(context):
    """
    Отправка сообщение об ошибке в Telegram.

    :param contex: контекст DAG.

    :return: None.
    """
    send_telegram_message(contex, False)