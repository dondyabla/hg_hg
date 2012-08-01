  $ "$TESTDIR/hghave" serve || exit 80
  $ "$TESTDIR/get-with-headers.py" localhost:$HGPORT 'rev/0'
   <li><a href="/shortlog/0cd96de13884">log</a></li>
   <li><a href="/graph/0cd96de13884">graph</a></li>
   <li><a href="/raw-rev/0cd96de13884">raw</a></li>
   <li><a href="/file/0cd96de13884">browse</a></li>
  <h2><a href="/">test</a></h2>
  <h3>changeset 0:0cd96de13884   </h3>
  <div id="hint">find changesets by author, revision,
  files, or words in the commit message</div>
   <td class="date age">Thu, 01 Jan 1970 00:00:00 +0000</td></tr>
      <a id="diffstatexpand" href="javascript:showDiffstat()"/>[<tt>+</tt>]</a>
        <a href="javascript:hideDiffstat()"/>[<tt>-</tt>]</a>
        <p>
        <table>  <tr class="parity0">
    <tr class="parity1">
  <div class="sourcefirst">   line diff</div>
  
  <div class="source bottomline parity0"><pre><a href="#l1.1" id="l1.1">     1.1</a> <span class="minusline">--- /dev/null	Thu Jan 01 00:00:00 1970 +0000
  </span><a href="#l1.2" id="l1.2">     1.2</a> <span class="plusline">+++ b/a	Thu Jan 01 00:00:00 1970 +0000
  </span><a href="#l1.3" id="l1.3">     1.3</a> <span class="atline">@@ -0,0 +1,1 @@
  </span><a href="#l1.4" id="l1.4">     1.4</a> <span class="plusline">+a
  </span></pre></div><div class="source bottomline parity1"><pre><a href="#l2.1" id="l2.1">     2.1</a> <span class="minusline">--- /dev/null	Thu Jan 01 00:00:00 1970 +0000
  </span><a href="#l2.2" id="l2.2">     2.2</a> <span class="plusline">+++ b/b	Thu Jan 01 00:00:00 1970 +0000
  </span><a href="#l2.3" id="l2.3">     2.3</a> <span class="atline">@@ -0,0 +1,1 @@
  </span><a href="#l2.4" id="l2.4">     2.4</a> <span class="plusline">+b
  </span></pre></div>
  $ "$TESTDIR/get-with-headers.py" localhost:$HGPORT 'raw-rev/0'
  $ "$TESTDIR/get-with-headers.py" localhost:$HGPORT 'diff/tip/b'
  <li><a href="/shortlog/559edbd9ed20">log</a></li>
  <li><a href="/graph/559edbd9ed20">graph</a></li>
  <li><a href="/rev/559edbd9ed20">changeset</a></li>
  <li><a href="/file/559edbd9ed20">browse</a></li>
  <li><a href="/file/559edbd9ed20/b">file</a></li>
  <li><a href="/comparison/559edbd9ed20/b">comparison</a></li>
  <li><a href="/annotate/559edbd9ed20/b">annotate</a></li>
  <li><a href="/log/559edbd9ed20/b">file log</a></li>
  <li><a href="/raw-file/559edbd9ed20/b">raw</a></li>
  <h2><a href="/">test</a></h2>
  <h3>diff b @ 1:559edbd9ed20</h3>
  <div id="hint">find changesets by author, revision,
  files, or words in the commit message</div>
  
  <div class="sourcefirst">   line diff</div>
  
  <div class="source bottomline parity0"><pre><a href="#l1.1" id="l1.1">     1.1</a> <span class="minusline">--- a/b	Thu Jan 01 00:00:00 1970 +0000
  </span><a href="#l1.2" id="l1.2">     1.2</a> <span class="plusline">+++ /dev/null	Thu Jan 01 00:00:00 1970 +0000
  </span><a href="#l1.3" id="l1.3">     1.3</a> <span class="atline">@@ -1,1 +0,0 @@
  </span><a href="#l1.4" id="l1.4">     1.4</a> <span class="minusline">-b
  </span></pre></div>
  $ "$TESTDIR/killdaemons.py"
  $ "$TESTDIR/get-with-headers.py" localhost:$HGPORT 'rev/0'
   <li><a href="/shortlog/0cd96de13884">log</a></li>
   <li><a href="/graph/0cd96de13884">graph</a></li>
   <li><a href="/raw-rev/0cd96de13884">raw</a></li>
   <li><a href="/file/0cd96de13884">browse</a></li>
  <h2><a href="/">test</a></h2>
  <h3>changeset 0:0cd96de13884   </h3>
  <div id="hint">find changesets by author, revision,
  files, or words in the commit message</div>
   <td class="date age">Thu, 01 Jan 1970 00:00:00 +0000</td></tr>
      <a id="diffstatexpand" href="javascript:showDiffstat()"/>[<tt>+</tt>]</a>
        <a href="javascript:hideDiffstat()"/>[<tt>-</tt>]</a>
        <p>
        <table>  <tr class="parity0">
    <tr class="parity1">
  <div class="sourcefirst">   line diff</div>
  
  <div class="source bottomline parity0"><pre><a href="#l1.1" id="l1.1">     1.1</a> new file mode 100644
  <a href="#l1.2" id="l1.2">     1.2</a> <span class="minusline">--- /dev/null
  </span><a href="#l1.3" id="l1.3">     1.3</a> <span class="plusline">+++ b/a
  </span><a href="#l1.4" id="l1.4">     1.4</a> <span class="atline">@@ -0,0 +1,1 @@
  </span><a href="#l1.5" id="l1.5">     1.5</a> <span class="plusline">+a
  </span></pre></div><div class="source bottomline parity1"><pre><a href="#l2.1" id="l2.1">     2.1</a> new file mode 100644
  <a href="#l2.2" id="l2.2">     2.2</a> <span class="minusline">--- /dev/null
  </span><a href="#l2.3" id="l2.3">     2.3</a> <span class="plusline">+++ b/b
  </span><a href="#l2.4" id="l2.4">     2.4</a> <span class="atline">@@ -0,0 +1,1 @@
  </span><a href="#l2.5" id="l2.5">     2.5</a> <span class="plusline">+b
  </span></pre></div>
  $ "$TESTDIR/get-with-headers.py" localhost:$HGPORT 'raw-rev/0'