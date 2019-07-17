from ripgrepy import Ripgrepy

rg = Ripgrepy('lol', '.').json().run()

print(rg.as_string)
print(rg.as_dict)
print(rg.as_json)
