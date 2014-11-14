cat $1 | grep 'z.*=' | awk 'BEGIN {OFS="\t"}{print $2, $3, $5}' | sed -E 's/\[//' | sed -E 's/\[//' | sed -E 's/\]//' | sed -E 's/\]//' > $2
