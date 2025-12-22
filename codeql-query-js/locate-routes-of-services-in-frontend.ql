import javascript

from
  YamlDocument doc,
  YamlMapping root,
  YamlMapping springMap,
  YamlMapping cloudMap,
  YamlMapping gatewayMap,
  YamlSequence routesSeq,
  YamlMapping routeMap,
  YamlString serviceLink,
  YamlSequence servicePredicatesSeq,
  YamlString servicePredicate,
  string serviceFrontendLink,
  string serviceName
where
  doc.getFile().getExtension() in ["yml", "yaml"] and
  root = doc.eval().(YamlMapping) and
  root.lookup("spring") = springMap and
  springMap.lookup("cloud") = cloudMap and
  cloudMap.lookup("gateway") = gatewayMap and
  gatewayMap.lookup("routes") = routesSeq and
  routesSeq.getAChild().(YamlMapping) = routeMap and
  routeMap.lookup("uri") = serviceLink and
  routeMap.lookup("predicates") = servicePredicatesSeq and
  servicePredicatesSeq.getAChild().(YamlString) = servicePredicate and
  servicePredicate.getValue().regexpCapture("Path=(.+)$", 1) = serviceFrontendLink and
  serviceLink.getValue().regexpCapture("lb://(.+)$", 1) = serviceName
select
  doc.getFile().getRelativePath(),
  serviceName,
  serviceFrontendLink
