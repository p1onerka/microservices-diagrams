import java

from Class c, Annotation ann_class, Annotation ann_method, Method m
where
  c = m.getDeclaringType() and
  ann_class = c.getAnAnnotation() and
  ann_class.getType().getQualifiedName().matches("%EnableDiscoveryClient") and
  ann_method = m.getAnAnnotation() and
  ann_method.getType().getQualifiedName().matches("%LoadBalanced")
select c
