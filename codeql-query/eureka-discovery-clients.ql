import java

// workaround. codeQL DB should be recompiled with all dependencies
from Class c, Annotation ann
where
    ann = c.getAnAnnotation() and
    ann.getType().getQualifiedName().matches("%EnableDiscoveryClient")
select c, c.getFile().getRelativePath()
