import gdb
import re
from gdb.FrameDecorator import FrameDecorator

class QmlStackTraceFrameFilter:
    def __init__(self):
        self.name = "QML stack trace"
        self.priority = 100
        self.enabled = True

        gdb.frame_filters[self.name] = self

    def filter(self, frame_iter):
        return QmlStackTraceIterator(frame_iter)

class QmlStackTraceIterator:
    def __init__(self, frame_iter):
        self.frame_iter = frame_iter
        self.execution_context = 0
        self.qml_frame_found = False

    def __iter__(self):
        return self

    def next(self):
        frame = next(self.frame_iter)

        args = frame.frame_args()
        if args:
            for arg in args:
                symbol = arg.symbol()
                if symbol.type.code == gdb.TYPE_CODE_PTR and \
                   symbol.type.target().name == "QV4::ExecutionContext":
                    self.execution_context = symbol.value(frame.inferior_frame())

        if self.qml_frame_found:
            return NullFrameDecorator()

        # First QML frame has PC pointing to an anonymous memory area (not
        # backed by any .so file).
        if gdb.solib_name(frame.inferior_frame().pc()) is None and \
           self.execution_context != 0:
            self.qml_frame_found = True
            return FinalFrameDecorator(frame, self.execution_context)

        return frame

class FinalFrameDecorator(FrameDecorator):
    frame_rexp = re.compile(r"""frame={level="(\d+)",
                                 func="([^"]*)",
                                 file="([^"]*)",
                                 fullname="([^"]*)",
                                 line="(\d*)",
                                 language="js"}""", re.VERBOSE)

    def __init__(self, frame, execution_context):
        super(self.__class__, self).__init__(frame)
        self.execution_context = execution_context

    def function(self):
        return "[QML]"

    def elided(self):
        v4stacktrace_symbol = gdb.lookup_global_symbol("qt_v4StackTrace");
        if v4stacktrace_symbol is None:
            return iter([])

        v4stacktrace = v4stacktrace_symbol.value();
        stacktrace_str = v4stacktrace(self.execution_context).string()

        elided_frames = []

        for match in self.__class__.frame_rexp.findall(stacktrace_str):
            elided_frames.append(QmlFrameDecorator(self.inferior_frame(), \
                                 match[1], match[2], match[4]))

        return iter(elided_frames)

class NullFrameDecorator:
    def inferior_frame(self):
        return None

class QmlFrameDecorator:
    def __init__(self, frame, function_name, function_filename, line):
        self.frame = frame
        self.function_name = function_name
        self.function_filename = function_filename
        self.function_line = int(line)

    def inferior_frame(self):
        return self.frame

    def function(self):
        return self.function_name

    def filename(self):
        return self.function_filename

    def line(self):
        return self.function_line

QmlStackTraceFrameFilter()
