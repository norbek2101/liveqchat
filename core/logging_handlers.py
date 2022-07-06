# from logging import Logger, FileHandler, Handler
import logging


class CustomHandler(logging.Handler):
    def emit(self, record) -> None:
        print('record : ', record)
        return super().emit(record)

# class CustomFileHandler(FileHandler):
#     def handleError(self, record) -> None:
#         print('record : ', record)
#         return super().handleError(record)


# class CustomLogger(Logger):

#     def info(self, msg: object, *args: object, exc_info = ..., stack_info  = ..., stacklevel: int = ..., extra = ...) -> None:
#         print(f'msg : {msg}')
#         print(f'args : {args}')
#         print(f'exc_info : {exc_info}')
#         print(f'stack_info : {stack_info}')
#         print(f'stacklevel : {stacklevel}')
#         print(f'extra : {extra}')
#         return super().info(msg, *args, exc_info=exc_info, stack_info=stack_info, stacklevel=stacklevel, extra=extra)
