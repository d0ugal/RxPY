import six
from six import add_metaclass

from rx.observable import Observable, Observer
from rx.anonymousobservable import AnonymousObservable
from rx.internal import ExtensionMethod

@add_metaclass(ExtensionMethod)
class ObservableDoAction(Observable):
    """Uses a meta class to extend Observable with the methods in this class"""

    def do_action(self, observer=None, on_next=None, on_error=None, on_completed=None):
        """Invokes an action for each element in the observable sequence and
        invokes an action upon graceful or exceptional termination of the
        observable sequence. This method can be used for debugging, logging,
        etc. of query behavior by intercepting the message stream to run
        arbitrary actions for messages on the pipeline.

        1 - observable.do_action(observer)
        2 - observable.do_action(on_next)
        3 - observable.do_action(on_next, on_error)
        4 - observable.do_action(on_next, on_error, on_completed)

        observer -- [Optional] Observer, or ...
        on_next -- [Optional] Action to invoke for each element in the
            observable sequence.
        on_error -- [Optional] Action to invoke upon exceptional termination
            of the observable sequence.
        on_completed -- [Optional] Action to invoke upon graceful termination
            of the observable sequence.

        Returns the source sequence with the side-effecting behavior applied.
        """
        source = self
        if not observer is None:
            if isinstance(observer, Observer):
                on_next = observer.on_next
                on_error = observer.on_error
                on_completed = observer.on_completed
            else:
                on_next = observer

        def subscribe(observer):
            def _on_next(x):
                try:
                    on_next(x)
                except Exception as e:
                    observer.on_error(e)

                observer.on_next(x)

            def _on_error(exception):
                if not on_error:
                    observer.on_error(exception)
                else:
                    try:
                        on_error(exception)
                    except Exception as e:
                        observer.on_error(e)

                    observer.on_error(exception)

            def _on_completed():
                if not on_completed:
                    observer.on_completed()
                else:
                    try:
                        on_completed()
                    except Exception as e:
                        observer.on_error(e)

                    observer.on_completed()
            return source.subscribe(_on_next, _on_error, _on_completed)
        return AnonymousObservable(subscribe)
