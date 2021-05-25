import pickle

PORT = 5050
HEADER = 16
FORMAT = 'utf-8'


def send_object(object, connection):
    pickled_obj = pickle.dumps(object)
    if len(pickled_obj) % HEADER != 0:
        pickled_obj += b' ' * (HEADER - len(pickled_obj) % HEADER)

    length_message = str(len(pickled_obj)).encode(FORMAT)
    length_message += b' ' * (HEADER - len(length_message))
    try:
        connection.send(length_message + pickled_obj)
    except ConnectionResetError as e:
        print('Connection lost.')


def get_object(connection):
    complete_data = b''
    object_len = 0
    object_len_received = False
    receiving_data = True
    while receiving_data:
        data = connection.recv(HEADER)
        if not object_len_received:
            object_len_received = True
            object_len = int(data[:HEADER])

        complete_data += data
        if len(complete_data) - HEADER == object_len:  # Data received
            receiving_data = object_len_received = False
            unpickled_obj = pickle.loads(complete_data[HEADER:])

    return unpickled_obj


def message_to_all(obj, connections):
    for conn in connections:
        if conn:
            send_object(obj, conn)
