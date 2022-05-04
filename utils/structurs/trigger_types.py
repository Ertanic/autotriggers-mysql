trigger_types = [
            {
                'type': 'INSERT',
                'message_log': "Добавлена запись",
                'time': 'AFTER'
            },
            {
                'type': 'UPDATE',
                'message_log': "Запись обновлена",
                'time': 'BEFORE'
            },
            {
                'type': 'DELETE',
                'message_log': "Запись удалена",
                'time': 'BEFORE'
            }
        ]