# Spark Week 6: Architecture & Performance Insights

## Architecture

### Three-Tier Execution Model
```
User Program
    ↓
Driver (orchestrator, DAG builder, task scheduler)
    ↓
Cluster Manager (YARN, Standalone, Kubernetes - allocates resources)
    ↓
Executors (worker processes - run tasks on partitions, cache data)
```

**Key:** Driver doesn't process data; it coordinates. Executors do the actual work.

---

### Client Mode vs Cluster Mode

| Aspect | Client Mode | Cluster Mode |
|--------|-------------|--------------|
| Driver location | Client machine | Inside cluster |
| Connection requirement | Must stay connected | Fire-and-forget |
| Resource usage | Client's CPU/RAM | Cluster's CPU/RAM |
| Use case | Dev/testing | Production |

**Choose Client for dev, Cluster for production jobs.**

---

## Performance: Lazy Evaluation & DAG

### Lazy Evaluation = Delayed Execution
```python
# None of these execute yet
df = spark.read.csv("data.csv")
df_filtered = df.filter(col("price") > 100)
df_selected = df_filtered.select("product_id", "price")

# Only NOW does execution happen (action triggered)
df_selected.show()
```

**Why it matters:**
- Spark combines all transformations into ONE optimized plan
- Eliminates redundant computations
- Reduces shuffle and I/O

### DAG: Directed Acyclic Graph
- Visual representation of all transformations
- Built lazily, optimized before execution
- If a worker fails, Spark can **recompute only the failed partition** (fault tolerance via lineage)

### Catalyst Optimizer
- Rewrites DAG to eliminate unnecessary operations
- Pushes filters down early (see Predicate Pushdown)
- Reorders operations for efficiency

---

## Storage: CSV vs Parquet

### CSV (Row-based)
```
Row 1: 1001, 2188.07, Electronics, ...
Row 2: 1002, 3745.5, Home, ...
Row 3: 1003, 3001.96, Sports, ...
```
- **Readable, human-friendly**
- **Slow:** Must read every column to access one
- **No schema encoding**
- **Larger file size**

### Parquet (Columnar)
```
Column 1: [1001, 1002, 1003, ...]
Column 2: [2188.07, 3745.5, 3001.96, ...]
Column 3: [Electronics, Home, Sports, ...]
```
- **Fast for analytics:** Read only needed columns
- **Compression:** Similar values cluster together
- **Schema embedded**
- **Smaller file size (~10x savings)**

**Rule:** Use Parquet for data lakes and pipelines. CSV only for small files or source data.

---

## Predicate Pushdown (Parquet)

Without optimization:
```
Read entire Parquet file → Filter rows where price > 1000
```

With Predicate Pushdown:
```
Filter rows where price > 1000 at read time → Read only matching blocks
```

**Result:** Massive I/O reduction. Catalyst pushes filters down automatically.

---

## Transformations vs Actions

### Transformations (Lazy — return DataFrame)
```python
df.filter(...)      # Returns new DF
df.select(...)      # Returns new DF
df.groupBy(...)     # Returns new DF
df.join(...)        # Returns new DF
```

### Actions (Eager — execute immediately)
```python
df.show()           # Triggers execution
df.collect()        # Triggers execution
df.count()          # Triggers execution
df.write.parquet()  # Triggers execution
```

**Pattern:** Chain transformations → trigger with ONE action.

---

## Memory: .show() vs .collect()

### .show(n)
```python
df.show(5)  # Display first 5 rows only
```
- Safe on terabyte datasets
- Reads sample, doesn't load full dataset to driver memory
- **Use for exploration**

### .collect()
```python
df.collect()  # Pull ALL rows to driver memory
```
- Dangerous on large datasets
- Can cause OutOfMemoryError on driver
- **Use only on small, known-size data**

---

## Fault Tolerance via Lineage

Spark tracks the **DAG lineage**:
```
Read CSV → Filter → Select → GroupBy
```

If Executor-2 crashes during GroupBy:
1. Spark knows which partitions GroupBy needs
2. Recomputes only those upstream partitions
3. Reattempts GroupBy
4. No need to reread or recompute other parts

**Lineage = automatic recovery.**

---

## Practical Performance Checklist

- [ ] Use **Parquet** for persistent data (not CSV)
- [ ] **Lazy eval:** Chain transformations, trigger with one action
- [ ] **Avoid .collect()** on large data; use .show() or limit()
- [ ] **Push filters early** in pipeline (Catalyst does this, but design accordingly)
- [ ] **Partition strategically** for large datasets (reduces shuffles)
- [ ] **Cache intermediate results** only if reused multiple times
- [ ] **Monitor executor memory** — OOM kills tasks
- [ ] **Use Client mode for dev, Cluster mode for production**

---

## Key Takeaways

1. **Architecture:** Driver coordinates, Executors compute, Cluster Manager allocates.
2. **Lazy Eval:** Transformations deferred until action; Catalyst optimizes the full plan.
3. **Parquet > CSV:** Columnar format 10x faster for analytics.
4. **Predicate Pushdown:** Read only needed data automatically.
5. **Transformations + Actions:** Chain lazy transforms, trigger with one action.
6. **Memory:** .show() safe, .collect() dangerous on big data.
7. **Fault Tolerance:** DAG lineage allows automatic partition recomputation.
