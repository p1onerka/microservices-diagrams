import java

from MethodCall mc
where mc.getMethod().getName() = "get"
//select mc.getReceiverType().getLocation()
select mc.getCompilationUnit(), mc.getCompilationUnit().getRelativePath()
//select mc.getCompilationUnit(), mc.getCompilationUnit().getPackage()
