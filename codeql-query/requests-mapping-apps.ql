// Copyright (c) 2026 Ksenia Kotelnikova
// SPDX-License-Identifier: MIT

import java

from Class c, Annotation ann
where
    ann = c.getAnAnnotation() and
    ann.getType().getQualifiedName().matches("%RequestMapping")
select c
