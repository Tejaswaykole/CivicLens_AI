# Frontend API contract

This document maps the React application on `main` to the Phase 3 API. The frontend was inspected from `main` and was not modified. It still reads mock data from `frontend/src/mock/data.ts` and `AppDataProvider`.

The API uses JSON with snake_case fields. The TypeScript models use camelCase. Phase 7 should map between them. This phase does not change the UI.

## Roles, statuses, and priorities

These values match `frontend/src/types/index.ts`.

| Frontend type | Allowed values |
| --- | --- |
| `UserRole` | `system_admin`, `grievance_officer`, `department_officer`, `citizen` |
| `ComplaintStatus` | `submitted`, `in_review`, `triaged`, `assigned`, `in_progress`, `resolved`, `rejected` |
| `ComplaintPriority` | `critical`, `high`, `medium`, `low` |
| Notification `type` | `urgent`, `info`, `success`, `alert` |

Complaint categories are the citizen form options:

- `Road Infrastructure`
- `Water & Sewage`
- `Electrical Hazard`
- `Sanitation & Solid Waste`
- `Street Lighting`

## Screens and the fields they use

### Citizen submission (`CitizenSubmitComplaintPage`)

The form collects `title`, `description`, `category`, `departmentId`, `locationAddress`, and `wardZone`. The location field is labeled "Location / Street Landmark"; the frontend stores that single string as `locationAddress`. There is no separate landmark column. The file input is a simulated upload and is not sent anywhere.

`addComplaint` also sends `citizenName`, `citizenContactMasked`, `resolutionDueAt`, and `status`. The provider then invents `trackingNumber`, `aiAssessment`, `effectivePriority`, and the first status-history row.

### Citizen and officer complaint views

Screens display `trackingNumber`, `title`, `description`, `category`, `status`, `locationAddress`, `wardZone`, `departmentName`, `citizenName`, `citizenContactMasked`, `effectivePriority`, `aiAssessment`, `humanConfirmation`, `assignedOfficerName`, `assignedCrewUnit`, `resolutionNotes`, `resolutionDueAt`, `statusHistory`, and sometimes `resolutionFeedback` and `imageUrl`.

### Human review (`OfficerHITLReviewPage`)

The queue is complaints whose mock `aiAssessment.requiresHITLReview` is true. Concurrence calls `concurComplaint(id, officerId, officerName, notes)`. Override calls `overrideComplaintPriority` and currently hard-codes the new priority to `high`. The page requires a review reason only for the override button.

### Department work orders (`DepartmentWorkOrdersPage`)

The screen filters the mock list to PWD, searches title, tracking number, and location, and filters status to `assigned`, `in_progress`, and `resolved`. The update dialog can submit any of those three statuses from the current row. The actor string is hard-coded in the page. `assignedCrewUnit` is displayed.

### Administration

User management searches name, email, and designation, filters by role, and locally creates, activates, and deletes users. Fields: `name`, `email`, `role`, `designation`, `wardOrZone`, `avatarInitials`, `isActive`. Department management edits `name`, `code`, `description`, `nodalOfficer`, `contactEmail`, and `slaTargetHours`, and shows stored `activeCasesCount` and `resolvedCount`.

Phase 3 does not implement those write operations. The API can list users and departments.

### Audit and notifications

The audit screen filters by `eventType` and searches description, actor name, and details. It labels every row as simulated and "Immutable Hash Verified". The API does not reproduce either claim.

`NotificationsPage` keeps its own copy of `MOCK_NOTIFICATIONS`. It does not read `AppDataContext`, so marks made there do not match the provider. Notification items have `title`, `message`, `type`, `read`, `createdAt`, and optionally `userId`, `role`, and `link`.

## Endpoint mapping

Base path: `/api/v1`. All of these routes are unauthenticated.

| Frontend behavior | Method and path | Phase 3 behavior |
| --- | --- | --- |
| App shell health is not implemented | `GET /health` | Reports process status and a real database check |
| User roster | `GET /users` | Paginated, filterable read |
| User profile row | `GET /users/{user_id}` | One user, without `password_hash` |
| Department cards | `GET /departments` | Paginated read with computed case counts |
| One department | `GET /departments/{department_id}` | Same shape |
| Complaint lists and search | `GET /complaints` | Paginated filters |
| Complaint detail and timeline | `GET /complaints/{complaint_id}` | Includes history, assignments, reviews, and stored predictions |
| `addComplaint` | `POST /complaints` | Creates a complaint and the first history row |
| `updateComplaintStatus` | `PATCH /complaints/{complaint_id}/status` | Validates the transition and appends history |
| Work-order assignment is embedded in mock rows | `POST /complaints/{complaint_id}/assignments` | Appends assignment history |
| `concurComplaint` / `overrideComplaintPriority` | `POST /complaints/{complaint_id}/reviews` | Stores a human decision and an audit event |
| Audit ledger | `GET /audit-logs` | Paginated operational events |
| Notification list | `GET /notifications` | Filter by recipient user, role, and read state |
| Mark one notification read | `PATCH /notifications/{notification_id}/read` | Idempotent |

There is no login, registration, prediction, or user-write endpoint.

## Request and response fields

### `POST /complaints`

```json
{
  "citizen_id": "uuid",
  "title": "Dark residential street",
  "description": "At least 10 characters.",
  "category": "Street Lighting",
  "location_address": "Lane 7 near the park",
  "ward_zone": "Development ward",
  "requested_department_id": "uuid or null"
}
```

`citizen_id` must refer to an active user. That check is not authentication. `requested_department_id` stores the citizen's selected line agency. It does not create an assignment and does not set the complaint's assigned department.

The response is a complaint detail:

| API field | Frontend field | Notes |
| --- | --- | --- |
| `id` | `id` | UUID, not `cmp_…` |
| `public_reference` | `trackingNumber` | `DEL-{UTC year}-{6 digits}` from a PostgreSQL sequence. The mock uses a random 4-digit suffix. |
| `title`, `description`, `category` | same names in camelCase | |
| `location_address` | `locationAddress` | Includes the landmark text the form collects |
| `ward_zone` | `wardZone` | Optional |
| `status` | `status` | Starts as `submitted` |
| `citizen` | `citizenName` | `{id, display_name, role, avatar_initials}` |
| `requested_department` | part of `departmentId` at submit time | `{id, code, name}` or null |
| `department` | `departmentId` / `departmentName` after assignment | Null until an assignment is recorded |
| `confirmed_priority` | `humanConfirmation.confirmedPriority`, and only then `effectivePriority` | Null when nobody has reviewed the complaint. The API does not copy a model priority into this field. |
| `resolution_notes` | `resolutionNotes` | Set when status becomes `resolved` |
| `resolution_due_at` | `resolutionDueAt` | Set from the department SLA when an assignment is created. It is not a fixed 48-hour placeholder. |
| `predictions` | `aiAssessment` | Empty unless a real prediction row exists. See below. |
| `reviews` | `humanConfirmation` | List, newest review is the source of `confirmed_priority` |
| `assignments` | `assignedOfficerName`, `assignedCrewUnit` | History, with `is_current` |
| `status_history` | `statusHistory` | See below |
| `created_at`, `updated_at` | `createdAt`, `updatedAt` | UTC timestamps |

Not returned, because the frontend currently fabricates them or has no stored source:

- `aiAssessment` as a whole, including `confidenceScore`, `urgencyReasoning`, `detectedCategories`, `flaggedSafetyHazard`, `requiresHITLReview`, and `influentialFeatures`
- `effectivePriority` when no human review exists
- `citizenContactMasked`
- `imageUrl`
- `resolutionFeedback`

A stored prediction, if a future model inserts one, is returned as:

```json
{
  "id": "uuid",
  "model_identifier": "string",
  "model_version": "string",
  "predicted_category": "string or null",
  "suggested_priority": "critical | high | medium | low | null",
  "confidence": "number from 0 to 1, or null",
  "explanation": "object or null",
  "predicted_at": "timestamp"
}
```

`confidence` is present only when that row has a value. The API does not calculate one.

### Status history

```json
{
  "id": "uuid",
  "previous_status": "submitted or null for the first row",
  "new_status": "triaged",
  "title": "Status changed from submitted to triaged",
  "note": "optional",
  "actor_user_id": "uuid or null",
  "actor_display_name": "string or null",
  "actor_label": "unverified text or null",
  "actor_verified": false,
  "created_at": "timestamp"
}
```

The frontend `actor` string and narrative titles such as "Officer Concurrence Recorded" are not stored. `title` is a factual transition label. `actor_verified` is always false in this phase.

### `PATCH /complaints/{complaint_id}/status`

```json
{
  "status": "in_progress",
  "note": "Required, at least 3 characters.",
  "actor_user_id": "optional uuid of an existing user",
  "actor_label": "optional unverified label"
}
```

Allowed transitions:

| From | To |
| --- | --- |
| `submitted` | `in_review`, `triaged`, `rejected` |
| `in_review` | `triaged`, `rejected` |
| `triaged` | `assigned`, `rejected` |
| `assigned` | `in_progress`, `resolved`, `rejected` |
| `in_progress` | `resolved`, `assigned` |
| `resolved`, `rejected` | none |

`assigned` to `resolved` is allowed because the department dialog can close a work order without a separate in-progress step. `submitted` to `resolved` is rejected. Any other jump returns HTTP 409 `invalid_status_transition`, and no history row is added.

The department dialog currently offers `assigned`, `in_progress`, and `resolved` even when the complaint is not in a state that can move there. Phase 7 needs to handle a 409 from that dialog.

### `POST /complaints/{complaint_id}/assignments`

```json
{
  "department_id": "uuid",
  "assigned_officer_id": "optional uuid",
  "assigned_crew_unit": "optional",
  "note": "optional",
  "actor_user_id": "optional uuid",
  "actor_label": "optional"
}
```

The complaint must be `triaged`, `assigned`, or `in_progress`. The department must exist and be active. An officer, when present, must be an active `department_officer`. If that user has a department, it must be the assigned department.

The first assignment from `triaged` moves the complaint to `assigned` and writes status history. A later assignment keeps the current status, marks the previous assignment `is_current: false`, and keeps both rows. `resolution_due_at` becomes the assignment time plus `sla_target_hours`.

### `POST /complaints/{complaint_id}/reviews`

```json
{
  "reviewer_user_id": "uuid of an active user",
  "suggested_priority": "optional",
  "confirmed_priority": "critical | high | medium | low",
  "justification": "required when the two priorities differ"
}
```

The complaint must be `submitted`, `in_review`, or `triaged`. A review from `submitted` or `in_review` moves it to `triaged`.

Rules:

- If the latest stored prediction has a suggested priority, that value is the suggestion. A different `suggested_priority` in the body returns HTTP 409 `suggestion_mismatch`. The request cannot rewrite the stored machine suggestion.
- If no prediction exists and the body includes `suggested_priority`, the review is stored with `suggestion_origin: client_supplied`. That is not a model output.
- If neither exists, `suggestion_origin` is `none` and `suggested_priority` is null.
- When the suggestion and the confirmed priority differ, `justification` must be at least 10 characters after trimming. The database enforces the same rule.
- The reviewer id is checked for existence only. Sending it does not authorize the caller.
- The audit action is `CONCURRENCE` when the priorities match, `HITL_OVERRIDE` when they differ, and `HUMAN_REVIEW` when there was no suggestion.

The frontend override button only offers `high`. The API accepts any of the four priorities.

### Users

`GET /users` query parameters: `role`, `is_active`, `department_id`, `q` (name, email, designation), `page`, `page_size`.

```json
{
  "id": "uuid",
  "display_name": "Dev Citizen",
  "email": "dev.citizen@example.com",
  "role": "citizen",
  "is_active": true,
  "department_id": null,
  "department": null,
  "designation": null,
  "ward_or_zone": "Development ward",
  "avatar_initials": "DC",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

| API | Frontend |
| --- | --- |
| `display_name` | `name` |
| `ward_or_zone` | `wardOrZone` |
| `avatar_initials` | `avatarInitials` (computed from the display name when omitted) |
| `department` | `departmentName` via the nested object |

`password_hash` is a nullable column for a future authentication phase. It is not in the schema and is not loaded for these reads.

### Departments

`GET /departments` query parameters: `is_active`, `q` (name or code), `page`, `page_size`.

| API | Frontend |
| --- | --- |
| `code`, `name`, `description` | same |
| `nodal_officer_name` | `nodalOfficer` |
| `contact_email` | `contactEmail` |
| `sla_target_hours` | `slaTargetHours` |
| `is_active` | not on the TypeScript type; defaults to true |
| `active_cases_count` | `activeCasesCount` |
| `resolved_count` | `resolvedCount` |

Counts are calculated. Active cases are complaints whose assigned department is this one and whose status is not `resolved` or `rejected`. Resolved counts are status `resolved` only. The mock numbers are not copied.

### Audit logs

`GET /audit-logs` filters: `action`, `entity_type`, `entity_id`, `actor_user_id`, `q` (summary or actor display name), `created_from`, `created_to`, `page`, `page_size`.

Actions written by this API:

- `COMPLAINT_CREATED`
- `STATUS_CHANGE`
- `ASSIGNMENT_CREATED`
- `CONCURRENCE`
- `HITL_OVERRIDE`
- `HUMAN_REVIEW`

The frontend also has `DEPARTMENT_UPDATE`, `USER_CREATE`, and `SYSTEM_ALERT`. Those are not emitted, because this phase has no department or user write API. `COMPLAINT_CREATED` is the registration event the mock called `SYSTEM_ALERT`.

`event_metadata` stores identifiers, status names, category, department code, and priority values. It does not store the complaint description, email addresses, or passwords. `actor_verified` is false. There is no hash and no `isSimulated` flag. The audit screen's cryptographic wording should not be connected to this API as if verification existed.

### Notifications

`GET /notifications` filters: `recipient_user_id`, `recipient_role`, `is_read`, `page`, `page_size`.

| API | Frontend |
| --- | --- |
| `notification_type` | `type` |
| `is_read` | `read` |
| `recipient_user_id` | `userId` |
| `recipient_role` | `role` |
| `link` | `link` |

A notification must have a user, a role, or both. Links stored by the API are relative paths such as `/app/officer/inbox`. Creating a complaint notifies the `grievance_officer` role with the reference and category, not the full description. Status changes notify the citizen user. An assignment notifies the assigned officer when one was named.

`PATCH /notifications/{notification_id}/read` sets `is_read` to true. Calling it again stays true. The frontend's separate "mark all read" control is not an endpoint yet.

## Pagination, filtering, and errors

List endpoints accept `page` (default 1) and `page_size` (default 20, maximum 100).

```json
{
  "items": [],
  "page": 1,
  "page_size": 20,
  "total": 0
}
```

Complaint list filters: `status`, `category`, `department_id` (the assigned department, not the citizen's requested department), `citizen_id`, `reference` (exact public reference), `q` (title, reference, location, ward), `created_from`, `created_to`.

There is no priority filter yet. The officer inbox filters on `effectivePriority`, which this API does not synthesize.

Errors use one shape. Request bodies are not echoed back.

```json
{
  "error": {
    "code": "not_found",
    "message": "Complaint not found.",
    "details": []
  }
}
```

| HTTP | `code` | When |
| --- | --- | --- |
| 404 | `not_found` | Unknown complaint, user, department, or notification |
| 409 | `invalid_status_transition` | Status or assignment is not allowed from the current status |
| 409 | `inactive_user` / `inactive_department` | The referenced row exists but is inactive |
| 409 | `invalid_officer` | Officer role or department does not match the assignment |
| 409 | `suggestion_mismatch` | Review tried to replace a stored model priority |
| 409 | `conflict` | A database uniqueness conflict. The SQL error is not returned. |
| 422 | `validation_error` | Field validation, including a missing override justification |
| 503 | `database_not_configured` / `database_unavailable` | No URL, or the database cannot be used |

Validation `details` contain `loc`, `message`, and `type` only.

## Smallest proposals where the frontend was ambiguous

- Citizen-selected agency is `requested_department_id`. Formal assignment is a separate history table. The mock stores one `departmentId` for both moments.
- `confirmed_priority` stays null until a human review. The mock `effectivePriority` falls back to the simulated AI priority; this API will not do that.
- Public references gained a 6-digit sequence so they stay unique without using the UUID.
- Department case counts are defined from assigned complaints, as above.
- Status titles are factual. The mock's longer titles are presentation copy.
- Notification copy omits the complaint description. The mock includes the title.
