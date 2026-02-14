# eval_artifacts

Esta carpeta contiene *snapshots* de artefactos de evaluación que se versionan para facilitar auditoría (por ejemplo, revisión por tribunal).

Reglas:
- `reports/` se considera output efímero/local y permanece ignorado por Git.
- `eval_artifacts/` contiene únicamente artefactos seleccionados (mínimos) que aportan valor para revisión sin ejecutar el pipeline.

Contenido actual:
- `ch07/` incluye el JSON de evaluación generativa y los outputs crudos por pregunta (`gen_XXX.txt`).
