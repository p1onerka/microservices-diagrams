import javascript

from
  YamlDocument doc,
  YamlMapping root,
  YamlMapping springMap,
  YamlMapping cloudMap,
  YamlMapping configMap,
  YamlMapping serverMap,
  YamlMapping gitMap,
  YamlString repoLink
where
  doc.getFile().getExtension() in ["yml", "yaml"] and
  root = doc.eval().(YamlMapping) and
  root.lookup("spring") = springMap and
  springMap.lookup("cloud") = cloudMap and
  cloudMap.lookup("config") = configMap and
  configMap.lookup("server") = serverMap and
  serverMap.lookup("git") = gitMap and
  gitMap.lookup("uri") = repoLink
select
  doc.getFile().getRelativePath(),
  repoLink.getValue()
