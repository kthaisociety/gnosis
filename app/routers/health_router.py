from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from datetime import datetime, timedelta

router = APIRouter(prefix="/health", tags=["Health Check"])

START_TIME_UTC = datetime.utcnow()

@router.get(
    "/", 
    summary="Health Check Dashboard", 
    description="Performs a health check.", 
    response_class=HTMLResponse
)
async def get_health():
    # Get the current time in UTC.
    current_time_utc = datetime.utcnow()
    
    # Calculate the timedelta since the application started.
    uptime_delta: timedelta = current_time_utc - START_TIME_UTC
    
    # Format the uptime into a human-readable string (e.g., "1 day, 4:05:10")
    # We split off the microseconds for a cleaner display
    human_readable_uptime = str(uptime_delta).split('.')[0]
    uptime_in_seconds = uptime_delta.total_seconds()
    
    status = "OK" # Static as of now
    status_color = "green"
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <!-- Page will refresh every 30 seconds -->
        <meta http-equiv="refresh" content="30" />
        <title>API Health Dashboard</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />
        <style>
            body {{
                font-family: 'Inter', sans-serif;
            }}
            /* Pulsing animations for status dot */
            @keyframes pulse-green {{
                0%, 100% {{
                    opacity: 1;
                    box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.7);
                }}
                50% {{
                    opacity: 1;
                    box-shadow: 0 0 0 10px rgba(34, 197, 94, 0);
                }}
            }}
            @keyframes pulse-red {{
                0%, 100% {{
                    opacity: 1;
                    box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7);
                }}
                50% {{
                    opacity: 1;
                    box-shadow: 0 0 0 10px rgba(239, 68, 68, 0);
                }}
            }}
            .pulse-green {{ animation: pulse-green 2s infinite; }}
            .pulse-red {{ animation: pulse-red 2s infinite; }}
        </style>
    </head>
    <body class="bg-gray-100 dark:bg-gray-900 text-gray-900 dark:text-gray-100 min-h-screen flex items-center justify-center p-4">
        <div class="w-full max-w-md bg-white dark:bg-gray-800 shadow-2xl rounded-2xl overflow-hidden border border-gray-200 dark:border-gray-700">
            <!-- Header -->
            <div class="p-6 border-b border-gray-200 dark:border-gray-700">
                <h1 class="text-2xl font-bold text-center">API Health</h1>
            </div>

            <!-- Body -->
            <div class="p-8 space-y-6">

                <!-- Status Card -->
                <div class="flex items-center justify-between p-6 bg-gray-50 dark:bg-gray-700 rounded-xl">
                    <h2 class="text-lg font-semibold">Status</h2>
                    <div class="flex items-center space-x-3">
                        <span class="relative flex h-4 w-4" id="status-dot-container">
                            <span class="absolute inline-flex h-full w-full rounded-full bg-{status_color}-400 opacity-75 pulse-{status_color}"></span>
                            <span class="relative inline-flex rounded-full h-4 w-4 bg-{status_color}-500"></span>
                        </span>
                        <span class="text-xl font-bold text-{status_color}-500 dark:text-{status_color}-400" id="status-text">{status}</span>
                    </div>
                </div>

                <!-- Uptime Metrics -->
                <div class="space-y-4">
                    <!-- Human Readable Uptime -->
                    <div class="p-6 bg-gray-50 dark:bg-gray-700 rounded-xl">
                        <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400">Uptime</h3>
                        <p class="mt-2 text-3xl font-semibold" id="uptime-human">{human_readable_uptime}</p>
                    </div>

                    <!-- Uptime in Seconds -->
                    <div class="p-6 bg-gray-50 dark:bg-gray-700 rounded-xl">
                        <h3 class="text-sm font-medium text-gray-500 dark:text-gray-400">Uptime (Seconds)</h3>
                        <p class="mt-2 text-3xl font-semibold" id="uptime-seconds">{uptime_in_seconds:,.2f}</p>
                    </div>
                </div>

            </div>

            <!-- Footer -->
            <div class="p-6 bg-gray-50 dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
                <p class="text-xs text-gray-500 dark:text-gray-400 text-center">
                    Last checked: <span id="last-checked">{current_time_utc}</span>
                </p>
            </div>
        </div>

        <!-- JavaScript to fetch data -->
        <script>
            // Get references to the elements we need to update
            const statusTextEl = document.getElementById('status-text');
            const statusDotContainerEl = document.getElementById('status-dot-container');
            const uptimeHumanEl = document.getElementById('uptime-human');
            const uptimeSecondsEl = document.getElementById('uptime-seconds');
            const lastCheckedEl = document.getElementById('last-checked');

            async function updateHealthData() {{
                try {{
                    const response = await fetch('/health/json');
                    if (!response.ok) {{
                        throw new Error('Network response was not ok');
                    }}
                    const data = await response.json();

                    // Update Status
                    const status = data.status || "ERROR";
                    const isOk = status === "OK";
                    const statusColor = isOk ? "green" : "red";

                    statusTextEl.textContent = status;
                    statusTextEl.className = `text-xl font-bold text-${{statusColor}}-500 dark:text-${{statusColor}}-400`;

                    // Update Status Dot
                    statusDotContainerEl.innerHTML = `
                        <span class="absolute inline-flex h-full w-full rounded-full bg-${{statusColor}}-400 opacity-75 pulse-${{statusColor}}"></span>
                        <span class="relative inline-flex rounded-full h-4 w-4 bg-${{statusColor}}-500"></span>
                    `;

                    // Update Uptime
                    uptimeHumanEl.textContent = data.uptime_human || 'N/A';

                    // Format seconds with commas
                    const secs = Number(data.uptime_seconds || 0);
                    uptimeSecondsEl.textContent = secs.toLocaleString('en-US', {{ minimumFractionDigits: 2, maximumFractionDigits: 2 }});

                    // Update Last Checked
                    lastCheckedEl.textContent = data.last_checked_utc || 'N/A';

                }} catch (error) {{
                    console.error('Failed to fetch health data:', error);
                    statusTextEl.textContent = 'ERROR';
                    statusTextEl.className = 'text-xl font-bold text-red-500 dark:text-red-400';
                    statusDotContainerEl.innerHTML = `
                        <span class="absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75 pulse-red"></span>
                        <span class="relative inline-flex rounded-full h-4 w-4 bg-red-500"></span>
                    `;
                    uptimeHumanEl.textContent = 'Error';
                    uptimeSecondsEl.textContent = 'Error';
                    lastCheckedEl.textContent = 'Failed to load';
                }}
            }}

            // Run immediately and every 3 seconds
            updateHealthData();
            setInterval(updateHealthData, 3000);
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content, status_code=200)


@router.get(
    "/json",
    summary="Get Health Status (JSON)",
    description="Returns API status and uptime in JSON format.",
)
async def get_health_json():
    """
    Provides a JSON endpoint for health check data.
    This is consumed by the HTML dashboard.
    """
    current_time_utc = datetime.utcnow()
    uptime_delta: timedelta = current_time_utc - START_TIME_UTC
    human_readable_uptime = str(uptime_delta).split('.')[0]
    
    return {
        "status": "OK",
        "uptime_seconds": uptime_delta.total_seconds(),
        "uptime_human": human_readable_uptime,
        "last_checked_utc": current_time_utc.strftime('%Y-%m-%d %H:%M:%S') + " UTC"
    }