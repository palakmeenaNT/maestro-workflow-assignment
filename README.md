# Mini-Maestro workflow simulation

The project keeps the four-task assignment workflow while separating the API in
the same style as Maestro: request/response schemas, validation dependencies,
services, handlers, and routers.

## API contracts

- `POST /workflows` validates and writes a generated DAG.
- `POST /run-workflow` triggers `sample_data_workflow` by default. Supply
  `{"dag_id": "your_dag", "conf": {...}}` to trigger another generated DAG.
- `GET /status?dag_id=sample_data_workflow` retrieves the last run.
- `GET /show-output` returns a typed response containing `processed_data`.

Every `python` task in the workflow definition must now declare its own
callable. The API validates that the source is Python and that it defines the
named function before rendering it into the DAG.

