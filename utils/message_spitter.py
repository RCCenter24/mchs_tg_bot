
async def split_message(message, max_length=4096):
    if len(message) <= max_length:
        return [message]

    messages = []
    while len(message) > max_length:
        split_index = message[:max_length].rfind('\n')
        if split_index == -1:
            split_index = max_length

        messages.append(message[:split_index])
        message = message[split_index:].lstrip()

    if message:
        messages.append(message)

    return messages