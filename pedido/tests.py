from django.test import TestCase

# Create your tests here.


session = {'carrinho': {

    '14': {'nome': 'A'},
    '15': {'nome': 'B'},
    '16': {'nome': 'C'},

}

}


if '3' in session['carrinho']:
    print('true')
else:
    print('false')
