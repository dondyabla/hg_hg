  $ "$TESTDIR/hghave" git || exit 80
  $ hg clone . ../tc
  $ hg clone . ../ta
  $ hg clone . ../tb
  $ hg clone . ../td
  $ hg clone ../t inner
  $ hg clone t d/t
  abort: subrepo s is missing
  abort: subrepo s is missing
  $ hg update -C
Sticky subrepositorys, file changes
  use (l)ocal source (da5f5b1) or (r)emote source (aa84837)?
   l
  $ hg update --clean tip > /dev/null 2>&1 
  use (l)ocal source (32a3438) or (r)emote source (da5f5b1)?
   l
  use (l)ocal source (32a3438) or (r)emote source (32a3438)?
   l