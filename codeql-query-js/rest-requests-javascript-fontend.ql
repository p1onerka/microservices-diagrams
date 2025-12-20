import javascript

from CallExpr call
where call.getCalleeName() = "get"
select call.getFile().getRelativePath(), call
