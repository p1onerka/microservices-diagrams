import javascript

from
  YamlDocument doc,
  YamlMapping root,
  YamlMapping springMap,
  YamlMapping appMap,
  YamlString nameVal
where
  doc.getFile().getExtension() in ["yml", "yaml"] and
  root = doc.eval().(YamlMapping) and
  root.lookup("spring") = springMap and
  springMap.lookup("application") = appMap and
  appMap.lookup("name") = nameVal
select
  doc.getFile().getRelativePath(),
  nameVal.getValue()
