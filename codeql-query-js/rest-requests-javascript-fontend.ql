import javascript

from CallExpr call, Expr s
where 
  call.getCalleeName() = "get" and
  call.getArgument(0) = s
select call.getFile().getRelativePath(), call, s, call.getArgument(0).getStringValue()
