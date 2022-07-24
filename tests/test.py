from ripgrepy import Ripgrepy

def test_base():
    rg = Ripgrepy('lol', '.').context(1).json().run()

    print(rg.as_string)
    print(rg.as_dict)
    print(rg.as_json)
