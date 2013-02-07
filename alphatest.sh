for ((i=11; i<=20; i++));
do
find . -name "*.pkl" -type f|xargs rm -f
echo "Alpha = " $i/10
python tweetAnalyzer.py $i
python tweetAnalyzer.py $i >> tester.txt
done
python deleteme.py tester.txt out.txt
