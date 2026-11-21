import sqlglot
from sqlglot import exp
from sqlglot.errors import ParseError
from app.schemas.validation import SQLValidationResult, ValidationStatus


class SQLValidatorService:
    FORBIDDEN_TYPES = (
        exp.Drop, exp.Delete, exp.Update, exp.Insert,
        exp.Alter, exp.Create, exp.Command, exp.Grant,
    )

    def validate(
        self,
        sql: str,
        dialect: str,
        allowed_schema_map: dict[str, list[str]],
        allowed_statements: list[str] | None = None,
        max_cost_limit: int = 10000,
        can_bypass_cost_limit: bool = False,
        language: str = "tr",
    ) -> SQLValidationResult:
        allowed_stmts = {s.upper() for s in (allowed_statements or ["SELECT"])}
        read_dialect = "sqlite" if dialect == "sqlite" else dialect

        try:
            expressions = sqlglot.parse(sql, read=read_dialect)
        except ParseError as exc:
            msg = f"SQL sözdizimi hatası: {exc}" if language == "tr" else f"SQL syntax error: {exc}"
            return SQLValidationResult(is_valid=False, status=ValidationStatus.BLOCKED_SYNTAX, block_reason=msg)

        valid_exprs = [e for e in expressions if e is not None]
        if len(valid_exprs) != 1:
            msg = "Tek sorgu kuralı ihlali (Stacked query engellendi)." if language == "tr" else "Multiple or empty statements blocked."
            return SQLValidationResult(is_valid=False, status=ValidationStatus.BLOCKED_SYNTAX, block_reason=msg)

        expr = next(iter(valid_exprs))

        stmt_type = expr.key.upper() if expr.key else ""
        if stmt_type not in allowed_stmts or list(expr.find_all(self.FORBIDDEN_TYPES)):
            msg = f"Yetkisiz veya yıkıcı SQL komutu engellendi: {stmt_type}" if language == "tr" else f"Destructive or unauthorized SQL command blocked: {stmt_type}"
            return SQLValidationResult(is_valid=False, status=ValidationStatus.BLOCKED_DDL_DML, block_reason=msg)

        cte_names = {cte.alias_or_name.lower() for cte in expr.find_all(exp.CTE)}
        normalized_schema = {k.lower(): {c.lower() for c in v} for k, v in allowed_schema_map.items()}
        alias_to_table: dict[str, str] = {}
        detected_tables: list[str] = []

        for tbl in expr.find_all(exp.Table):
            t_name = tbl.name.lower()
            if t_name in cte_names:
                continue
            detected_tables.append(t_name)
            if tbl.alias:
                alias_to_table[tbl.alias.lower()] = t_name
            alias_to_table[t_name] = t_name

            if t_name not in normalized_schema:
                msg = f"RBAC / Halüsinasyon Engeli: '{t_name}' tablosuna erişim yetkiniz yok." if language == "tr" else f"RBAC / Hallucination Block: Access denied to table '{t_name}'."
                return SQLValidationResult(
                    is_valid=False,
                    status=ValidationStatus.BLOCKED_RBAC,
                    block_reason=msg,
                    detected_tables=detected_tables,
                )

        if list(expr.find_all(exp.Star)):
            msg = "Güvenlik Politikası: 'SELECT *' kullanımı yasaktır, sütunları açıkça belirtin." if language == "tr" else "Security Policy: 'SELECT *' is forbidden; specify columns explicitly."
            return SQLValidationResult(
                is_valid=False,
                status=ValidationStatus.BLOCKED_RBAC,
                block_reason=msg,
                detected_tables=detected_tables,
            )

        detected_columns: list[str] = []
        allowed_all_cols = set().union(*normalized_schema.values()) if normalized_schema else set()

        for col in expr.find_all(exp.Column):
            c_name = col.name.lower()
            detected_columns.append(c_name)
            t_ref = col.table.lower() if col.table else None

            if t_ref and t_ref in alias_to_table:
                real_tbl = alias_to_table[t_ref]
                if c_name not in normalized_schema.get(real_tbl, set()):
                    msg = f"RBAC Engeli: '{real_tbl}.{c_name}' sütununa erişim yetkiniz yok." if language == "tr" else f"RBAC Block: Access denied to column '{real_tbl}.{c_name}'."
                    return SQLValidationResult(
                        is_valid=False,
                        status=ValidationStatus.BLOCKED_RBAC,
                        block_reason=msg,
                        detected_tables=detected_tables,
                        detected_columns=detected_columns,
                    )
            elif c_name not in allowed_all_cols and c_name not in cte_names:
                msg = f"RBAC / Halüsinasyon Engeli: '{c_name}' sütunu izinli şemada bulunamadı." if language == "tr" else f"RBAC / Hallucination Block: Column '{c_name}' not in allowed schema."
                return SQLValidationResult(
                    is_valid=False,
                    status=ValidationStatus.BLOCKED_RBAC,
                    block_reason=msg,
                    detected_tables=detected_tables,
                    detected_columns=detected_columns,
                )

        cost = 100
        for j in expr.find_all(exp.Join):
            cost += 5000 if (j.args.get("kind") or "").upper() == "CROSS" else 500
        cost += len(list(expr.find_all(exp.Subquery))) * 400
        if expr.args.get("where") is None and expr.args.get("limit") is None:
            cost += 3000

        if cost > max_cost_limit and not can_bypass_cost_limit:
            msg = f"Maliyet Limiti Aşıldı: Tahmini maliyet ({cost}) şirket limitini ({max_cost_limit}) aşıyor." if language == "tr" else f"Cost Limit Exceeded: Estimated cost ({cost}) exceeds limit ({max_cost_limit})."
            return SQLValidationResult(
                is_valid=False,
                status=ValidationStatus.BLOCKED_COST,
                block_reason=msg,
                detected_tables=detected_tables,
                detected_columns=detected_columns,
                estimated_cost=cost,
            )

        sanitized = expr.sql(dialect=read_dialect)
        return SQLValidationResult(
            is_valid=True,
            status=ValidationStatus.APPROVED,
            sanitized_sql=sanitized,
            detected_tables=detected_tables,
            detected_columns=detected_columns,
            estimated_cost=cost,
        )