package fissh

import (
	"log"
	"strings"
	"strconv"
)

func filtByDate(id, date string) []string {
	var filenames []string
	for _, filename := range ListFishMediaSlice(id, true, true) {
		if strings.HasPrefix(filename, date) {
			filenames = append(filenames, filename)
		}
	}
	return filenames
}

func filtByLatestVid(id, count string) []string {
	var filenames []string = ListFishMediaSlice(id, true, false)
	c, err := strconv.Atoi(count)
	if err != nil {
		log.Fatal(err)
	}
	return filenames[len(filenames) - c:] 
}

func filtByLatestPic(id, count string) []string {
	var filenames []string = ListFishMediaSlice(id, false, true)
	c, err := strconv.Atoi(count)
	if err != nil {
		log.Fatal(err)
	}
	return filenames[len(filenames) - c:] 
}

func filtByTagged(id string) [] string {
	var filenames []string
	for _, filename := range ListFishMediaSlice(id, true, true) {
		if strings.HasSuffix(filename, ".ok") {
			filenames = append(filenames, filename)
		}
	}
	return filenames
}

func filtByUnTagged(id string) [] string {
	var filenames []string
	for _, filename := range ListFishMediaSlice(id, true, true) {
		if strings.HasSuffix(filename, ".mp4") || strings.HasSuffix(filename, ".png"){
			filenames = append(filenames, filename)
		}
	}
	return filenames
}
