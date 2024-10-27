import json
from math import factorial
from urllib.parse import parse_qs


def fibonacci(n: int) -> int:
    if n == 0:
        return 0
    elif n in [1,2]:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)
    

def mean(arr: list) -> float:
    return sum(arr)/len(arr)


async def get_request_body(receive):

    body = b''
    more_body = True

    while more_body:
        message = await receive()
        body += message.get('body', b'')
        more_body = message.get('more_body', False)
    return body


async def send_response(send, status, body):

    if isinstance(body, dict):

        body = json.dumps(body)
        content = b'application/json'
    
    else:

        body = str(body)
        content = b'text/plain'

    await send({
        'type': 'http.response.start',
        'status': status,
        'headers': [
            [b'content-type', content],
        ],
    })

    await send({
        'type': 'http.response.body',
        'body': str(body).encode('utf-8')
    })

async def app(scope, receive, send):

    if scope['method'] != 'GET':
        status = 404
        body = 'Not Found'

        await send_response(send, status, body)
    else:

        our_path = scope['path'].strip('/').split('/')
        our_method = our_path[0]

        if our_method== 'factorial':

            try:

                n = int(parse_qs(scope['query_string'].decode('utf-8')).get('n')[0])
                if n < 0:

                    status = 400
                    body = 'Bad Request'

                else:
                    status = 200
                    body = {'result': factorial(n)}

                await send_response(send, status, body)

            except:

                status = 422
                body = 'Unprocessed entity'

                await send_response(send, status, body)
        elif our_method == 'fibonacci':

            if len(our_path) == 2:
                if not our_path[1].lstrip('-').isdigit():

                    status = 422 
                    body = 'Unprocessable Entity'

                else:
                    n = int(our_path[1])
                    if n < 0:

                        status = 400
                        body = 'Bad Request'

                    else:

                        status = 200
                        body = {'result': fibonacci(n)}

            else:

                status = 404
                body = 'Not Found'

            await send_response(send, status, body)

        elif our_method == 'mean':

            body = await get_request_body(receive)  

            try:
                array = json.loads(body.decode('utf-8'))
                
                if not array:
                    status = 400
                    body = 'Bad Request'

                    await send_response(send, status, body)
                else:
                    status = 200
                    body = {'result': mean(array)}

                    await send_response(send, status, body)

            except json.JSONDecodeError:

                status = 422
                body = 'Unprocessable Entity'

                await send_response(send, status, body)
        else:

            status = 404
            body = 'Not Found'

            await send_response(send, status, body)
