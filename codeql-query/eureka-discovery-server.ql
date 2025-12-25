import java

from Class c, Annotation ann
where
    ann = c.getAnAnnotation() and
    ann.getType().getQualifiedName().matches("%EnableEurekaServer")
select c, c.getFile().getRelativePath()
