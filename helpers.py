from py_mini_racer import py_mini_racer


def get_pass(e, t):
    return e + t - 15 if e % 2 == 0 else e + t - 109


class JSCodeExecutor(object):
    ctx = py_mini_racer.MiniRacer()
    ctx.eval("const window = {};")

    @staticmethod
    def prepare_context(server_url):
        JSCodeExecutor.ctx.eval("window.location = '{}';".format("coins.vk.ru"))

    @staticmethod
    def exec(code):
        return JSCodeExecutor.ctx.eval(code)
