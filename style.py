green1 = '97ba66'
green2 = 'A7D489'

def headline1():
    return """
    font: bold;
    font-size: 16px;
    color: black
    """


def headline2():
    return """
    font: bold;
    font-size: 14px;
    color: black
    """


def grey1():
    return """
    background-color: lightgrey
    """


def body1():
    return """
    font: bold;
    """

def body2():
    return """
    color: black
    """

def box1():
    return """
        QGroupBox {
        background-color:#97ba66;
        font:16pt Arial;
        font-weight: bold;
        color:white;
        border:2px solid gray;
        border-radius:10px;
        margin: 2px;
        }
        QGroupBox::title {
            left: 4px;
            top: 4px;
        }
    """

def box2():
    return """
        QGroupBox {
        background-color:#E5E4E2;
        border:2px;
        border-radius:5px;
        }
    """

def box3():
    return """
        QGroupBox {
        border:0px solid gray;
        border-radius:1px;
        }
    """

