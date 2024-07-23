package fissh 

import (
    "fmt"
)

func FormatBytes(bytes int64) string {
    const (
        KB = 1 << 10 // 1024
        MB = 1 << 20 // 1024 * 1024
        GB = 1 << 30 // 1024 * 1024 * 1024
        TB = 1 << 40 // 1024 * 1024 * 1024 * 1024
    )

    if bytes < KB {
        return fmt.Sprintf("%dB", bytes)
    } else if bytes < MB {
        return fmt.Sprintf("%.2fKB", float64(bytes)/KB)
    } else if bytes < GB {
        return fmt.Sprintf("%.2fMB", float64(bytes)/MB)
    } else if bytes < TB {
        return fmt.Sprintf("%.2fGB", float64(bytes)/GB)
    } else {
        return fmt.Sprintf("%.2fTB", float64(bytes)/TB)
    }
}
