# python-gtk-utils #

A collection of utilities ready to be `git subtree`-ed into a Python
GTK+ project  
<https://github.com/jefferyto/python-gtk-utils>  
0.1.0

All bug reports, feature requests and miscellaneous comments are welcome
at the [project issue tracker][].

## Installation ##

Use `git subtree` to pull this sub-project into your project:

```sh
git remote add python-gtk-utils https://github.com/jefferyto/python-gtk-utils.git
git subtree add --prefix=path/to/code/utils --squash python-gtk-utils master
```

Import into your code:

```python
from .utils import connect_handlers, disconnect_handlers
```

Pull for updates:

```sh
git subtree pull --prefix=path/to/code/utils --squash python-gtk-utils master
```

## Documentation ##

...would be a good idea ;-)

## License ##

Copyright &copy; 2013 Jeffery To <jeffery.to@gmail.com>

Available under GNU General Public License version 3


[project issue tracker]: https://github.com/jefferyto/python-gtk-utils/issues
