# Pymal: Mal in Python 3 #

Pymal is an implementation of Mal [(Make-a-Lisp)](https://github.com/kanaka/mal) in Python 3. It is obviously not the only such implementation, nor do I claim it is in any way better than any existing implementation. I primarily wrote it in order to learn Python.

The interpreter is self-hosting, i.e., it can run the Mal implementation of Mal. The only aspect that has not been implemented is metadata for builtin functions and composite types. (Only user-defined functions support metadata.) Furthermore, since the error messages are different from what the Mal tests expect, some of the step 9 tests don’t pass.
