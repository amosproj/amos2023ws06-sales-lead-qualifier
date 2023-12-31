# SPDX-License-Identifier: MIT
# SPDX-FileCopyrightText: 2023 Berkay Bozkurt <resitberkaybozkurt@gmail.com>

from queue import Queue
from threading import Lock, Thread
from typing import Any

from messenger import Message, MessageType, create_data_message

from logger import get_logger

log = get_logger()


class ControllerMeta(type):

    """
    Thread safe singleton implementation of Controller
    """

    _instances = {}  # Dictionary to store instances of Controller
    _lock: Lock = Lock()  # A lock to ensure thread-safety when creating instances

    def __call__(cls, *args: Any, **kwds: Any):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(
                    *args, **kwds
                )  # Create a new instance of Controller
                cls._instances[
                    cls
                ] = instance  # Store the instance in the _instances dictionary

        return cls._instances[cls]  # Return the instance of Controller


class Controller(metaclass=ControllerMeta):
    """
    Controller class with message processing and sending functionality.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self._finish_flag = False
        self._finish_flag_lock = Lock()
        self._message_queue: Queue[Message] = Queue(0)  # Queue for processing messages
        self._routing_queue: Queue[Message] = Queue(0)  # Queue for routing messages
        self._message_queue_processor_thread: Thread = (
            None  # Thread for processing messages
        )
        self._routing_queue_processor_thread: Thread = (
            None  # Thread for routing messages
        )
        self._start_message_queue_processing_thread()  # Start the message processing thread
        self._start_routing_queue_processing_thread()  # Start the routing thread

    def _message_queue_processor(self):
        while True:
            # do read operation with lock to get latest value
            with self._finish_flag_lock:
                # if set True then exit loop
                if self._finish_flag:
                    break
            if not self._message_queue.empty():
                try:
                    # Get a message from the message queue and process it‚
                    msg = self._message_queue.get()
                    # Simulate processing of the message
                    log.debug(f"Processing on {msg}")
                    self._enqueue_routing(msg)
                    # Simulate completion of processing
                    log.debug(f"Processed {msg}")
                # Handle any errors during message processing
                except Exception as e:
                    log.error(f"Error while processing message: {e}")
                finally:
                    # Mark the task as done in the processing queue
                    self._message_queue.task_done()
        log.debug(f"Message queue processor thread exited.")

    def _routing_queue_processor(self):
        while True:
            with self._finish_flag_lock:
                if self._finish_flag:
                    break
            if not self._routing_queue.empty():
                try:
                    # Mark the task as done in the processing queue
                    msg = self._routing_queue.get()
                    log.debug(f"Routing {msg}")
                    if msg.data_type == MessageType.DATA:
                        self._route_to_EVP(msg)
                    elif msg.data_type == MessageType.PREDICTION:
                        self._route_to_BDC(msg)
                    else:
                        log.warning(f"Unknown message type: {msg.data_type}")
                    log.debug(f"Routed {msg}")
                # Handle any errors during message routing
                except Exception as e:
                    log.error(f"Error while routing message: {e}")
                finally:
                    # Mark the task as done in the processing queue
                    self._routing_queue.task_done()
        log.debug(f"Routing queue processor thread exited.")

    # Start the message processing thread
    def _start_message_queue_processing_thread(self):
        if (
            not self._message_queue_processor_thread
            or not self._message_queue_processor_thread.is_alive()
        ):
            self._message_queue_processor_thread = Thread(
                target=self._message_queue_processor, daemon=True
            )
            self._message_queue_processor_thread.start()

    # Start the message routing thread
    def _start_routing_queue_processing_thread(self):
        if (
            not self._routing_queue_processor_thread
            or not self._routing_queue_processor_thread.is_alive()
        ):
            self._routing_queue_processor_thread = Thread(
                target=self._routing_queue_processor, daemon=True
            )
            self._routing_queue_processor_thread.start()

    def _route_to_BDC(self, msg: Message):
        # TODO call the method of base data collector
        return

    def _route_to_EVP(self, msg: Message):
        # TODO call the method of estimated value predictor
        return

    # Enqueue a message in the processing queue
    def _enqueue_message(self, msg: Message):
        self._message_queue.put(msg)

    # Enqueue a message in the routing queue
    def _enqueue_routing(self, msg: Message):
        self._routing_queue.put(msg)

    # Public interface to send a message
    def send_message(self, msg: Message):
        """
        processes message, forwards to related components.
        """
        if not self._finish_flag:
            self._enqueue_message(msg)
        else:
            log.debug(f"Controller finished can not send messages... ")

    def finish(self):
        """
        finishes controller, after all waiting messages are processed and routed
        """

        # wait till queues are empty.
        while not self._message_queue.empty() or not self._routing_queue.empty():
            log.debug(
                f"Waiting for message and routing threads to finish their jobs... "
            )

        with self._finish_flag_lock:
            # Set the finish flag to signal threads to stop
            self._finish_flag = True

        log.debug(f"Finishing threads... ")

        # Wait for the message queue processing thread to finish
        if (
            self._message_queue_processor_thread
            and self._message_queue_processor_thread.is_alive()
        ):
            log.debug(f"Finishing message queue processor thread...")
            self._message_queue_processor_thread.join()
        # Wait for the routing queue processing thread to finish
        if (
            self._routing_queue_processor_thread
            and self._routing_queue_processor_thread.is_alive()
        ):
            log.debug(f"Finishing routing queue processor thread...")
            self._routing_queue_processor_thread.join()

        # check if there are any elements in queues, if not, all cool!
        log.debug(f"Threads finished... ")
        log.debug(f"routing queue size... {self._routing_queue.unfinished_tasks}")
        log.debug(f"message queue size... {self._message_queue.unfinished_tasks}")
