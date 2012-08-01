  > graphlog=
  $ EDITED="$TESTTMP/editedhistory"
  $ cat > $EDITED <<EOF
  > pick 177f92b77385 c
  > pick e860deea161a e
  > pick 652413bf663e f
  > pick 055a42cdd887 d
  > EOF
  #  f, fold = use commit, but fold into previous commit (combines N and N-1)
  @  changeset:   5:853c68da763f
  o  changeset:   4:26f6a030ae82
  o  changeset:   3:b069cc29fb22
  $ cat > $EDITED <<EOF
  > pick 853c68da763f d
  > pick b069cc29fb22 e
  > pick 26f6a030ae82 f
  $ HGEDITOR="cat \"$EDITED\" > " hg histedit 177f92b77385 2>&1 | fixbundle
  @  changeset:   5:652413bf663e
  o  changeset:   4:e860deea161a
  o  changeset:   3:055a42cdd887
  $ cat > $EDITED <<EOF
  > pick 055a42cdd887 d
  > pick 652413bf663e f
  > pick e860deea161a e
  $ HGEDITOR="cat \"$EDITED\" > " hg histedit 177f92b77385 2>&1 | fixbundle
  @  changeset:   5:99a62755c625
  o  changeset:   4:7c6fdd608667
  o  changeset:   3:c4f52e213402
  o  changeset:   2:bfe4a5a76b37
  $ cat > $EDITED <<EOF
  > pick bfe4a5a76b37 d
  > pick c4f52e213402 f
  > pick 99a62755c625 c
  > pick 7c6fdd608667 e
  $ HGEDITOR="cat \"$EDITED\" > " hg histedit bfe4a5a76b37 --keep 2>&1 | fixbundle
  > cat > $EDITED <<EOF
  > pick 7c6fdd608667 e
  > pick 99a62755c625 c
  > EOF
  @  changeset:   7:99e266581538
  o  changeset:   6:5ad36efb0653
  |  parent:      3:c4f52e213402
  | o  changeset:   5:99a62755c625
  | o  changeset:   4:7c6fdd608667
  o  changeset:   3:c4f52e213402
  o  changeset:   2:bfe4a5a76b37
  $ hg histedit --commands "$EDITED" --rev -2 2>&1 | fixbundle
  @  changeset:   7:99e266581538
  o  changeset:   6:5ad36efb0653
  |  parent:      3:c4f52e213402
  | o  changeset:   5:99a62755c625
  | o  changeset:   4:7c6fdd608667
  o  changeset:   3:c4f52e213402
  o  changeset:   2:bfe4a5a76b37