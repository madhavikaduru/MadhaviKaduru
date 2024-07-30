/**
Finding maximum circular subarray sum
using kadane's algorithm (with O(n) time complexity)
 */

#incluse<iosteam>
#incluse<climits>
using namespace std;

int kadane(int arr[], int n)
{
    int currentsum = 0;
    int maxsum = INT_MIN;
    
    for(int i=0;i<n;i++)
    {
        currentsum+=arr[i];
        if(currentsum < 0)
            currentsum = 0;
        maxsum = max(maxsum,currentsum);
    }
    return maxsum;
}

int main() {
    // Define array arr[]
    int arr[] = {4,-4, 6, -6, 10, -11, 12}
    
    // Get size of array arr[]
    int n = sizeof(arr)/sizeof(arr[0]);
    
    // We calculate both wrap sum and non wrap sum
    int wrapsum, nonwrapsum;
    
    //get non wrap sum
    nonwrapsum= kadane(arr,n);
    
    //get wrap sum
    //  - get total sum
    //  - reverse sings in array and get 
    //    non contributing element sum with kadane
    int totalsum = 0;
    for(int i=0;i<n;i++)
    {
        totalsum+=arr[i];
        arr[i]=-arr[i];
    }
    
    //"wrapsum" = "total elements sum" - "sum of non-contributing element in finding max subarray sum"
    // As  non-contributing element are negative - on - becomes +
    // Hence addition below
    wrapsum = totalsum+kadane(arr,n);
    
    // Maximum of the two sums is what we want
    cout<< max(wrapsum, nonwrapsum)<<endl;
    
    return 0;
} // End of main(){}
