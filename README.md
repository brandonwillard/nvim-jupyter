# nvim-jupyter

Flexible [neovim] - [Jupyter] kernel interaction. Augments [neovim] with the following
functionality:

- `(c) JConnect [--existing filehint]` - **first connect to kernel**

  connect to new or existing kernel (using the `[--existing filehint]`)
  argument, where `[filehint]` is either the `*` (star) in `kernel-*.json`
  or the absolute path of the connection file.

- `(c) [range]JExecute`

  send current line to be executed by the kernel or if `[range]` is given
  execute the appropriate lines.

Legend `(c)` = command


## installation (_not ready for use_)

For whoever feels adventurous enough, I highly recommend [`vim-plug`].

For manual installation (_not recommended_):

```bash
git clone git@github.com:razvanc87/nvim-jupyter.git
ln -sf $HOME/nvim-jupyter $HOME/.nvim
```

_After installation_ don't forget to run `:UpdateRemotePlugins` in [neovim]!


## motivation

One of my primary motives for working on this plugin is to have a very clean
base and easy to understand and modify plugin design. Great care is taken for
the plugin to be highly modular and (ultimately) customizable without
overwhelming the user with hundreds of options.

Another reason is that, the other plugins offering the same functionality don't
quite use the powerful `Python` libraries. For example, [`vim-ipython`] has
a very rudimentary way of dealing with _vim_ command arguments which makes it
difficult to further improve and expand and at the moment it looks like
a spaghetti code. [`nvim-jupyter`] on the other hand, makes use from the very
beginning of the [argparse] `Python` module, making it extremely easy to
further add functionality to the [neovim] registered commands. Now this isn't
to say that [`vim-ipython`] isn't a good plugin. Hardly! It actually is very
good and without it I wouldn't even have started working on [`nvim-jupyter`] in
the first place!

The last reason I'd like to share with the world is: for a while now I wanted
to give back to the community. Many years I've only used other's products and
I think it's time to put my knowledge to the test and produce something useful
for this great open-source community. This being said, I raise the bar pretty
high with this first attempt and I hope I won't let anyone down!


## features

- simple and clean

- highly modular and flexible design for easy extensibility

- uses powerful built-in `Python` features to the full ([argparse] module,
  `dict` type for very simple yet powerful feedback generation, etc. _check the
  code!_)

- decoupled functionality ([neovim] - [Jupyter] communication managed by the
  main module class, with the rest of the functionality implemented in
  a separate modules) leading to separation of concerns

- always working with the latest technology. This deserves a little
  explanation. I have never understood how conservative the `Python` community
  is and how reluctant it was to move on to `Python 3`. I understand that some
  project can't _just_ upgrade, it's a long process, but it was never about
  just the projects, people, users... they also behaved like this. I am the
  adept of staying in the front lines of development and embrace change as it
  happens. So I make the claim that this package (for as long as I'll work on
  it) will work with the latest [Jupyter] releases. At the moment it only works
  with [Jupyter] `v4-dev` version which isn't ready for users, but I have
  a feeling by the time I finish implementing most of the features in this
  plugin, [Jupyter] would have moved from the `dev` stage and into
  mass-production. _This being said, now the bad news (maybe!)._ I will not
  work on implementing functionality for all versions of `IPython`, [Jupyter]
  in existence! My hope is that I will be able to keep up with [Jupyter]'s
  development and have the plugin always up to date for use with the latest
  version. It _will not be_ an objective to maintain support for older
  versions.


## objectives

- [ ] local kernel communication
- [ ] remote kernel communication
- [ ] work with any kernel
- [x] work from any file (not just programming language source files)
- [ ] for `ipykernel` work with `%matplotlib inline` seamlessly
- [ ] collaborative work?!

Stay tuned, more to come!

[neovim]: https://github.com/neovim/neovim
[Jupyter]: https://github.com/jupyter/jupyter
[`vim-ipython`]: https://github.com/ivanov/vim-ipython
[`nvim-jupyter`]: https://github.com/razvanc87/nvim-jupyter
[argparse]: https://docs.python.org/3/library/argparse.html
[`vim-plug`]: https://github.com/junegunn/vim-plug
