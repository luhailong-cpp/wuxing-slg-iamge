using System;
using UnityEngine;

// Candidate route playback only. One existing SE still slides; no walking animation,
// combat events, dynamic pathfinder or production controller is supplied.
public sealed class WuxingMapAssemblyRouteDemo : MonoBehaviour
{
    public SpriteRenderer unitRenderer;
    public Vector2[] routeTopLeft;
    public float worldHeightPixels = 960, pixelsPerUnit = 100;
    public float speedPixelsPerSecond = 150, waitAtStartSeconds = 0.25f;
    public bool playOnStart = true;
    public event Action FrameObserved; // Optional diagnostic observer, never a combat event.
    public Vector2 FootTopLeft { get; private set; }
    public int TargetIndex { get; private set; }
    public int RuntimeUpdateCount { get; private set; }
    public bool Finished { get; private set; }
    public bool Paused { get; private set; }
    private float wait;

    private void Start() { RestartRoute(); Paused = !playOnStart; }
    [ContextMenu("Restart candidate route")]
    public void RestartRoute()
    {
        if (routeTopLeft == null || routeTopLeft.Length == 0) return;
        FootTopLeft = routeTopLeft[0]; TargetIndex = 1;
        Finished = false; Paused = false; wait = waitAtStartSeconds;
        PlaceUnit();
    }
    [ContextMenu("Pause or resume candidate route")]
    public void TogglePause() { Paused = !Paused; }
    private void Update()
    {
        RuntimeUpdateCount++;
        #if ENABLE_LEGACY_INPUT_MANAGER
        if (Input.GetKeyDown(KeyCode.Space)) TogglePause();
        if (Input.GetKeyDown(KeyCode.R)) RestartRoute();
        #endif
        if (routeTopLeft == null || routeTopLeft.Length < 2 || Finished || Paused) return;
        if (wait > 0) { wait -= Time.deltaTime; return; }
        float budget = speedPixelsPerSecond * Time.deltaTime;
        while (budget > 0 && TargetIndex < routeTopLeft.Length)
        {
            Vector2 next = routeTopLeft[TargetIndex];
            float distance = Vector2.Distance(FootTopLeft, next);
            if (distance <= budget)
            {
                FootTopLeft = next; budget -= distance; TargetIndex++;
            }
            else
            {
                FootTopLeft = Vector2.MoveTowards(FootTopLeft, next, budget); budget = 0;
            }
        }
        Finished = TargetIndex >= routeTopLeft.Length;
        PlaceUnit();
    }
    private void LateUpdate() { FrameObserved?.Invoke(); }
    private void PlaceUnit()
    {
        if (unitRenderer == null) return;
        unitRenderer.transform.position = new Vector3(FootTopLeft.x / pixelsPerUnit,
            (worldHeightPixels - FootTopLeft.y) / pixelsPerUnit, 0);
        unitRenderer.sortingOrder = Mathf.RoundToInt(FootTopLeft.y * 10) + 1;
    }
}
