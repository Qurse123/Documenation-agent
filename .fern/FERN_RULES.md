---
description: Rules for editing Fern Definition files
globs: *.{yml,yaml}
---
Here are the rules for making a Fern definition file. Anytime you are prompted to edit or create a Fern definition file, you must stricly refer to these rules.

Additionally, you must always analyze the errors.yml and domain.yml (if they exist), so that you
are aware of any types that should reused. You must analyze both errors and domain before editing the fern definition file.

Your output must be the text for a valid Fern definition file, do not include any other text or comments.
Include standard CRUD operations and follow the pattern shown in the example below:

Path parameters are used for GET, PUT, and DELETE and the path parameter should be camelCase.

For dictionaries with unknown value types, use the map<string, unknown> type.

Here are some example types:
- uuid
- string
- integer
- datetime
- boolean
- list<T>
- optional<T>
- T
- map<K, V>

For any request that has query-parameters, a request name is required.
The request name should be the name of the endpoint, followed by "Request".
The request definition is not needed in types if query-parameters are present.
If an endpoint has no return type (i.e. DELETE), do not include a response field in the Fern definition for that endpoint

You must follow the example format exactly, do not include any other variations of Fern definition.

ALWAYS only include compilable python code, do not include any other text.
DO NOT include any comments or other text outsideof the code.
NO NOT include any reasoning or explanation of the code.
YOU MUST include errors.yml in your imports.

Example of format of the compilable Fern definition text:


imports:
  errors: errors.yml

service:
  auth: true
  base-path: /sample-object
  endpoints:
    CreateSampleObject:
      method: POST
      path: ""
      request: SampleObjectRequest
      response: SampleObject
      errors:
        - errors.NotAuthorizedError

    GetSampleObject:
      method: GET
      path: /{sampleObjectId}
      path-parameters:
        sampleObjectId: uuid
      response: SampleObject
      errors:
        - errors.NotAuthorizedError
        - errors.NotFoundError

    GetSampleObjects:
      docs: Retrieve the list of SampleObjects
      method: GET
      path: ""
      request:
        name: GetSampleObjectsRequest
        query-parameters:
          maxPageSize: optional<integer>
          nextPageToken: optional<string>
      response: SampleObjectsPage
      errors:
        - errors.NotAuthorizedError

    UpdateSampleObject:
      method: PATCH
      path: /{sampleObjectId}
      path-parameters:
        sampleObjectId: uuid
      request: UpdateSampleObjectRequest
      response: SampleObject
      errors:
        - errors.NotAuthorizedError
        - errors.NotFoundError

    DeleteSampleObject:
      method: DELETE
      path: /{sampleObjectId}
      path-parameters:
        sampleObjectId: uuid
      errors:
        - errors.NotAuthorizedError
        - errors.NotFoundError

types:
  SampleObject:
    properties:
      id: uuid

  SampleObjectRequest:
    properties:
      sampleObject: SampleObject

  UpdateSampleObjectRequest:
    properties:
      updatedSampleObject: SampleObject
      
  SampleObjectsPage:
    properties:
      items: list<SampleObject>
      nextPageToken: optional<string>
