<script lang="ts">
  import { beforeUpdate, getContext, tick } from 'svelte';
  import { get } from 'svelte/store';
  import type {
    TabularDataStore,
    Row,
  } from '@mathesar/stores/table-data/types';

  import type {
    Sorting,
    Filtering,
    Grouping,
    Pagination,
  } from '@mathesar/stores/table-data';
  import RowComponent from './row/Row.svelte';
  import Resizer from './virtual-list/Resizer.svelte';
  import VirtualList from './virtual-list/VirtualList.svelte';

  const tabularData = getContext<TabularDataStore>('tabularData');

  let virtualListRef: VirtualList;

  $: ({ id, recordsData, display, meta } = $tabularData);
  $: ({ sorting, filtering, grouping, pagination } = meta);
  $: ({ newRecords } = recordsData);
  $: ({ rowWidth, horizontalScrollOffset, scrollOffset, displayableRecords } =
    display);

  let initialSorting: Sorting;
  let initialFiltering: Filtering;
  let initialGrouping: Grouping;
  let initialPagination: Pagination;

  beforeUpdate(() => {
    initialSorting = get(sorting);
    initialFiltering = get(filtering);
    initialGrouping = get(grouping);
    initialPagination = get(pagination);
  });

  $: {
    if (
      initialSorting !== $sorting ||
      initialFiltering !== $filtering ||
      initialGrouping !== $grouping ||
      initialPagination !== $pagination
    ) {
      virtualListRef?.ScrollToTop();
    }
  }

  let previousNewRecordsCount = 0;

  async function resetIndex(_displayableRecords: Row[]) {
    const allRecordLength = _displayableRecords?.length;
    const newRecordLength = get(newRecords)?.length || 0;
    if (allRecordLength && previousNewRecordsCount !== newRecordLength) {
      const index = Math.max(allRecordLength - newRecordLength - 3, 0);
      await tick();
      if (previousNewRecordsCount < newRecordLength) {
        // eslint-disable-next-line @typescript-eslint/no-unsafe-call
        virtualListRef?.scrollToBottom();
      }
      previousNewRecordsCount = newRecordLength;
      // eslint-disable-next-line @typescript-eslint/no-unsafe-call
      virtualListRef?.resetAfterIndex(index);
    }
  }

  $: void resetIndex($displayableRecords);

  function getItemSize(index: number) {
    const defaultRowHeight = 30;
    const allRecords = get(displayableRecords);
    if (allRecords?.[index]?.isNewHelpText) {
      return 24;
    }

    // TODO: Check and set extra height for group. Needs UX rethought.
    return defaultRowHeight;
  }

  function checkAndResetActiveCell(e: Event) {
    const target = e.target as HTMLElement;
    // Use this class for elements attached out of cell element
    // which are part of cell interaction
    if (target.closest('.retain-active-cell')) {
      return;
    }

    const targetMissing = !document.body.contains(target);
    let clearActiveCell = false;

    if (targetMissing) {
      const focusedElementNotWithinEditableCell =
        !document.activeElement ||
        !document.activeElement.closest('.editable-cell');
      clearActiveCell = focusedElementNotWithinEditableCell;
    } else {
      const targetNotWithinEditableCell = !target.closest('.editable-cell');
      clearActiveCell = targetNotWithinEditableCell;
    }

    if (clearActiveCell) {
      display.resetActiveCell();
    }
  }
</script>

<svelte:window
  on:keydown={checkAndResetActiveCell}
  on:mousedown={checkAndResetActiveCell}
/>

<div class="body" tabindex="-1">
  <Resizer let:height>
    {#key id}
      <VirtualList
        bind:this={virtualListRef}
        bind:horizontalScrollOffset={$horizontalScrollOffset}
        bind:scrollOffset={$scrollOffset}
        {height}
        width={$rowWidth}
        itemCount={$displayableRecords.length}
        paddingBottom={30}
        itemSize={getItemSize}
        itemKey={(index) => recordsData.getIterationKey(index)}
        let:items
      >
        {#each items as it (it?.key || it)}
          {#if it && $displayableRecords[it.index]}
            <RowComponent
              style={it.style}
              bind:row={$displayableRecords[it.index]}
            />
          {/if}
        {/each}
      </VirtualList>
    {/key}
  </Resizer>
</div>
