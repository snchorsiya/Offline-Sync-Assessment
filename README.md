# Offline Survey Sync – API Automation & Testing

## 1. Project Overview

This project focuses on testing an offline survey application where field workers can collect survey data without an active internet connection and synchronize the data with the backend when connectivity is restored.

The primary testing challenge is handling duplicate local IDs, retry requests, concurrent synchronization, and data integrity when multiple devices collect data independently while offline.

### Scenario

Two field workers, Ankit and Pooja, survey the same village independently:

* Ankit registers **Govt Primary School** at 10:00 AM while offline.
* His device assigns the local ID `School_1`.
* Pooja registers the same school at 11:00 AM while also offline.
* Her device can also assign the local ID `School_1`.
* Both devices synchronize their data with the backend later.
* The backend must handle the duplicate local ID without overwriting one worker's survey data with the other's.
* If Ankit's synchronization request is retried, the backend should process it idempotently and should not create duplicate records.

The assignment also requires considering backend behavior when approximately **50,000 users synchronize data concurrently**, as well as Android background synchronization under poor or unstable network conditions.

---

## 2. Objectives

The main objectives of this test implementation are to verify:

1. Successful synchronization of valid offline survey data.
2. Handling of the same `local_id` from different devices.
3. Prevention of data overwriting during synchronization.
4. Idempotent retry behavior using the same `sync_id`.
5. Validation of missing required request fields.
6. Data integrity after multiple synchronization requests.
7. Android background synchronization behavior under poor network conditions.
8. Recovery when network connectivity is interrupted during a large file/photo upload.
9. Backend performance considerations for approximately 50,000 concurrent users.

---

## 3. Tools & Technologies

| Tool                                 | Purpose                                     |
| ------------------------------------ | ------------------------------------------- |
| Postman                              | API automation and validation               |
| Postman Mock Server / Local Mock API | Simulating the synchronization API          |
| JavaScript                           | Postman test assertions                     |
| ADB                                  | Android device/network testing              |
| Charles Proxy                        | Network interception and failure simulation |
| Git / GitHub                         | Source control and submission               |

---

## 4. Project Structure

```text
Offline-Sync-Assessment/
│
├── README.md
│
├── mock-server/
│   └── [Mock Server JSON / configuration files]
│
├── postman/
│   ├── Offline_Sync_API_Tests.json
│   └── Offline_Sync_Environment.json
│
└── test-plan/
    └── Offline_Sync_API_Test_Plan.xlsx
```

### Folder Description

* `README.md` – Project documentation, testing approach, and strategy.
* `mock-server/` – Files required for the local mock API setup.
* `postman/Offline_Sync_API_Tests.json` – Postman collection containing automated API tests.
* `postman/Offline_Sync_Environment.json` – Postman environment variables.
* `test-plan/Offline_Sync_API_Test_Plan.xlsx` – Detailed test cases and test plan.

---

# 5. API Automation

## API Under Test

The synchronization flow is tested using:

```text
POST /sync-survey
```

The API accepts survey information collected by a field worker while offline.

Example request structure:

```json
{
  "sync_id": "sync-ankit-001",
  "device_id": "device-ankit-001",
  "worker_id": "worker-ankit",
  "local_id": "School_1",
  "survey_data": {
    "school_name": "Govt Primary School",
    "village": "Village A",
    "students_count": 120
  },
  "updated_at": "2026-09-21T10:00:00Z"
}
```

---

## 6. Postman Collection

The Postman collection contains the following requests:

```text
Offline Sync API Tests
│
├── 01 - Create Ankit Survey
├── 02 - Create Pooja Survey - Same Local ID
├── 03 - Retry Ankit Survey - Idempotency
├── GET - Verify Survey Records
├── 04 - Invalid Request - Missing Device ID
└── 05 - Invalid Request - Missing Local ID
```

### Test Coverage

#### 01 - Create Ankit Survey

Validates the initial synchronization of Ankit's survey.

Assertions include:

* HTTP status is `201 Created`.
* Response status is `success`.
* `sync_id` matches the request.
* `local_id` is `School_1`.
* Correct `device_id` is returned.
* A `server_id` is generated.

#### 02 - Create Pooja Survey - Same Local ID

Pooja uses the same local ID:

```text
local_id = School_1
```

but has a different device:

```text
device_id = device-pooja-001
```

The test verifies that Pooja's survey is handled independently and does not overwrite Ankit's survey.

#### 03 - Retry Ankit Survey - Idempotency

The same synchronization request is sent again using:

```text
sync_id = sync-ankit-001
```

The expected behavior is that the server recognizes the already synchronized request and does not create another survey record.

The response remains associated with the original:

```text
sync_id
server_id
local_id
device_id
```

#### GET - Verify Survey Records

The GET request verifies the stored survey records after synchronization.

Expected result:

* Two survey records exist.
* Ankit's record exists.
* Pooja's record exists.
* Both records have different `server_id` values.
* Ankit's data is not overwritten by Pooja's data.

#### 04 - Invalid Request - Missing Device ID

A request is sent without `device_id`.

Expected result:

```text
HTTP 400 Bad Request
status = error
```

The error response should identify that `device_id` is required.

#### 05 - Invalid Request - Missing Local ID

A request is sent without `local_id`.

Expected result:

```text
HTTP 400 Bad Request
status = error
```

The error response should identify that `local_id` is required.

---

# 7. Duplicate Local ID & Data Collision Strategy

A local ID generated on an offline device should not be treated as a globally unique identifier.

For example:

| Worker | Device ID          | Local ID   | Sync ID          | Server ID      |
| ------ | ------------------ | ---------- | ---------------- | -------------- |
| Ankit  | `device-ankit-001` | `School_1` | `sync-ankit-001` | `srv-e90bded3` |
| Pooja  | `device-pooja-001` | `School_1` | `sync-pooja-001` | `srv-0e9e0cab` |

Although both devices generated:

```text
School_1
```

they are different local records because they originated from different devices.

The backend should therefore maintain a server-side unique identity rather than using `local_id` alone.

A suitable logical identification strategy is:

```text
device_id + local_id
```

for identifying a device-local record, while:

```text
sync_id
```

is used for synchronization idempotency.

This prevents Pooja's synchronization from overwriting Ankit's survey.

---

# 8. Idempotency & Retry Handling

Offline applications may retry synchronization because of:

* Temporary network failures.
* Request timeouts.
* App backgrounding.
* Device connectivity changes.
* Server response not reaching the client.

The same synchronization request may therefore reach the backend multiple times.

The test uses:

```text
sync_id = sync-ankit-001
```

as an idempotency key.

When the same request is retried:

1. The server checks whether the `sync_id` was already processed.
2. If it was processed, the server does not create another survey record.
3. The existing server record is returned.
4. The original data remains unchanged.

This prevents duplicate records caused by client retries.

---

# 9. Test Execution

## Prerequisites

Before running the collection:

1. Start the local mock server.
2. Ensure the mock API is available on:

```text
http://localhost:3000
```

3. Import the Postman collection.
4. Import/select the Postman environment.
5. Verify the following environment variables:

```text
baseUrl       = http://localhost:3000
ankitSyncId   = sync-ankit-001
poojaSyncId   = sync-pooja-001
```

## Run Individual Tests

Each request can be executed individually from the Postman collection.

## Run Complete Collection

Use **Postman Collection Runner** and execute the requests in the following order:

```text
01 - Create Ankit Survey
02 - Create Pooja Survey - Same Local ID
03 - Retry Ankit Survey - Idempotency
GET - Verify Survey Records
04 - Invalid Request - Missing Device ID
05 - Invalid Request - Missing Local ID
```

The collection contains automated assertions in the **Tests** section of each request.

---

# 10. Android Background Sync Testing Strategy

The mobile application should be tested for synchronization when the application is running in the background.

Important scenarios include:

### Scenario 1 – App Goes to Background

1. Create survey data while offline.
2. Put the application in the background.
3. Restore network connectivity.
4. Verify that synchronization starts according to the application's background-sync mechanism.
5. Verify that the survey is synchronized successfully.

### Scenario 2 – App Is Force-Stopped / Restarted

1. Create survey data while offline.
2. Close/restart the application.
3. Restore network connectivity.
4. Verify that unsynchronized records are still available.
5. Verify that synchronization resumes without data loss.

### Scenario 3 – Network Changes

Test transitions such as:

```text
Wi-Fi → Mobile Data
Mobile Data → Wi-Fi
Connected → Disconnected
Disconnected → Connected
```

The application should not lose locally stored survey data during these transitions.

---

# 11. Poor Network Testing

Poor network conditions are important because survey data may include photos or other large files.

The following conditions should be tested:

* High latency.
* Slow network.
* Intermittent connectivity.
* Connection drop during upload.
* Network recovery during synchronization.
* Multiple retry attempts.

The expected behavior is:

* Local survey data remains safe.
* Failed synchronization is retryable.
* Successfully uploaded data is not uploaded again unnecessarily.
* A retry does not create duplicate records.
* The user receives an appropriate synchronization status.

---

# 12. Network Failure at 99% Photo Upload

One important edge case is a network failure when a photo upload reaches approximately **99% completion**.

### Test Steps

1. Create a survey containing a photo.
2. Start synchronization.
3. Monitor the photo upload.
4. Interrupt the network when the upload reaches approximately 99%.
5. Verify the application's behavior.
6. Restore network connectivity.
7. Trigger or wait for retry.
8. Verify that the upload completes successfully.
9. Verify that the survey is synchronized only once.

### Expected Result

The application should not mark the photo as successfully uploaded when the final upload operation has not been confirmed by the server.

After network recovery, the application should either:

* Resume the upload if resumable upload is supported, or
* Safely retry the upload.

The retry must not result in corrupted files or duplicate survey records.

---

# 13. Charles Proxy Usage

Charles Proxy can be used to inspect and control API/network traffic between the Android application and backend.

Useful scenarios include:

* Inspecting synchronization requests.
* Adding network latency.
* Throttling bandwidth.
* Blocking specific requests.
* Simulating connection failures.
* Verifying request retries.
* Inspecting HTTP status codes and response payloads.

For example, the synchronization request can be interrupted during a large photo upload to reproduce the 99% network failure scenario.

---

# 14. ADB Usage

Android Debug Bridge (ADB) can be used for device-level testing and troubleshooting.

Useful commands/scenarios include:

```bash
adb devices
```

Verify that the Android device/emulator is connected.

```bash
adb logcat
```

Monitor application logs during synchronization.

Network connectivity can also be controlled using emulator/device configuration or appropriate Android test setup to simulate offline and online transitions.

ADB logs can help identify:

* Background sync execution.
* Retry attempts.
* Upload failures.
* Application crashes.
* Connectivity changes.
* Synchronization state transitions.

---

# 15. 50,000 Concurrent Users – Backend Load Strategy

The requirement states that approximately **50,000 users may synchronize data simultaneously**.

Postman functional automation is not intended to generate this level of load.

For this scenario, a dedicated performance/load testing tool such as **JMeter, k6, or Gatling** should be used.

### Suggested Load Test

Simulate:

```text
50,000 concurrent users
        ↓
POST /sync-survey
        ↓
Backend
        ↓
Database / Storage
```

The test should gradually increase traffic instead of immediately sending all requests.

### Metrics to Monitor

* Requests per second.
* Response time.
* Average latency.
* P95/P99 latency.
* Error rate.
* HTTP 4xx/5xx responses.
* CPU utilization.
* Memory utilization.
* Database connection usage.
* Database query latency.
* Queue depth, if asynchronous processing is used.

### Important Data Integrity Scenarios

The load test should also include:

* Different users using the same `local_id`.
* Same `sync_id` retried multiple times.
* Multiple synchronization requests for the same device.
* Simultaneous synchronization of different devices.
* Network retries during high server load.

The objective is to verify both **performance and data consistency** under concurrent synchronization.

---

# 16. Test Plan

Detailed test cases are maintained separately in:

```text
test-plan/Offline_Sync_API_Test_Plan.xlsx
```

The test plan covers:

* Positive API scenarios.
* Duplicate local ID collision.
* Idempotent retry.
* Data integrity.
* Negative validation.
* Network recovery.
* Concurrent synchronization.

---

# 17. Current API Automation Coverage

| Test ID | Scenario                               | Type           | Automation       |
| ------- | -------------------------------------- | -------------- | ---------------- |
| TC-001  | Create Ankit Survey                    | Positive       | Postman          |
| TC-002  | Create Pooja Survey with Same Local ID | Collision      | Postman          |
| TC-003  | Retry Ankit Survey                     | Idempotency    | Postman          |
| TC-004  | Verify Survey Records                  | Data Integrity | Postman          |
| TC-005  | Missing Device ID                      | Negative       | Postman          |
| TC-006  | Missing Local ID                       | Negative       | Postman          |
| TC-007  | Verify Ankit Data Not Overwritten      | Data Integrity | API verification |
| TC-008  | Verify Pooja Data Independently        | Data Integrity | API verification |
| TC-009  | Retry After Temporary Network Failure  | Recovery       | Strategy         |
| TC-010  | Simultaneous Synchronization           | Concurrency    | Strategy         |

---

# 18. Key Testing Considerations

The main risks identified for this scenario are:

1. Treating `local_id` as globally unique.
2. Overwriting one worker's data with another worker's data.
3. Creating duplicate records during retries.
4. Losing locally stored data when network connectivity changes.
5. Incorrectly marking an incomplete upload as successful.
6. Synchronization failures when the application is in the background.
7. Backend performance degradation under high concurrent synchronization traffic.

The test strategy addresses these risks through API automation, data-integrity validation, mobile network testing, retry testing, and a dedicated load-testing strategy.

---

# 19. Conclusion

The implemented Postman automation validates the core offline synchronization scenarios, including duplicate local IDs, idempotent retries, data integrity, and invalid request handling.

The additional mobile and performance strategy covers real-world conditions such as background synchronization, unstable networks, interrupted photo uploads, and high concurrent synchronization traffic.

The overall approach is designed to ensure that offline-collected survey data remains **consistent, recoverable, and protected from unintended overwrites or duplicate synchronization**.
