import java

from MethodCall mc, StringLiteral address
where (mc.getMethod().getName() = "get" or mc.getMethod().getName() = "post") and
    address.getCompilationUnit() = mc.getCompilationUnit() and
    address.getValue().indexOf("http://") >= 0
select mc.getCompilationUnit(), mc.getCompilationUnit().getRelativePath(), address.getValue()
